import random
import asyncio
from threading import Thread
from functools import partial
from django.db import transaction, IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from matchmaking.models import GameSession
from pong_app.consumers import broadcast_message
from .models import (TournamentParticipant, TournamentRound, TournamentMatch, MatchParticipant)
from .blockchain import set_tournament_in_blockchain


def add_participant_to_tournament(tournament, user):
    """
    Registers a user as a participant in a tournament if there is available space. It attempts to create a new
    TournamentParticipant object linking the user to the specified tournament. If the tournament has reached its
    maximum size, or if the user is already registered in the tournament, it fails gracefully.

    Parameters: tournament (Tournament): The tournament instance to add the participant to.
                user (User): The user instance to register as a participant.
    Returns: bool: True if the user is successfully added as a participant, False otherwise.
    """
    if tournament.participants.count() < tournament.size:
        try:
            with transaction.atomic():
                # Ensures that if any of the database operations fail, none of them will be executed.
                TournamentParticipant.objects.create(tournament=tournament, user=user)
                user.tournament_id = tournament.id
                user.save()
                run_async_task_in_thread(broadcast_message, f"tournament_{tournament.id}",
                                         {'type': 'tournament_message',
                                          'message': f"{user.username} has joined the tournament."})
            return True
        except IntegrityError:
            # This happens if the user is already registered in the tournament.
            # Comes from the unique_together in the TournamentParticipant model.
            return False
    else:
        # Tournament is full
        return False


def start_tournament(tournament):
    """
    Initiates the tournament if it's in 'open' status and fully populated with participants.
    Sets the tournament status to 'in progress' and triggers the creation of tournament rounds and matches.

    Args:
        tournament (Tournament): The tournament instance to start.
    """
    if tournament.status == 'open' and tournament.participants.count() == tournament.size:
        tournament.status = 'in progress'
        tournament.save()
        create_tournament_rounds_and_matches(tournament)


def create_tournament_rounds_and_matches(tournament):
    """
    Generates rounds and matches for the tournament based on the number of participants.
    Shuffles participants for random match assignments in the first round, and schedules the first round.

    Args:
        tournament (Tournament): The tournament for which rounds and matches are created.
    """
    participants = list(tournament.participants.all())
    total_rounds = 2 if len(participants) == 4 else 3

    random.shuffle(participants)

    with transaction.atomic():
        for round_number in range(1, total_rounds + 1):
            print(f"Creating round {round_number} matches...")
            round_status = 'scheduled' if round_number == 1 else 'created'
            tournament_round = TournamentRound.objects.create(
                tournament=tournament,
                number=round_number,
                status=round_status
            )
            create_matches_for_round(tournament_round, participants, round_number)
            if round_number == 1:
                schedule_round(tournament_round)


def create_matches_for_round(tournament_round, participants, round_number):
    """
    Creates matches for a given tournament round. Directly pairs participants in the first round,
    and prepares matches for subsequent rounds without assigning participants immediately.

    Args:
        tournament_round (TournamentRound): The round for which matches are being created.
        participants (list): List of tournament participants, shuffled for the first round.
        round_number (int): The current round number, used to determine pairing and scheduling.
    """
    # Number of matches halves each round for a single-elimination tournament
    num_matches = 2 ** (2 - round_number)

    with transaction.atomic():
        for i in range(num_matches):
            match_status = 'scheduled' if round_number == 1 else 'created'

            match = TournamentMatch.objects.create(
                round=tournament_round,
                status=match_status,
                number=i + 1
            )

            players = [participants[i * 2].user, participants[i * 2 + 1].user] if round_number == 1 else [None, None]
            MatchParticipant.objects.create(match=match, player=players[0], is_ready=False)
            MatchParticipant.objects.create(match=match, player=players[1], is_ready=False)


def schedule_round(round):
    """
    Schedules a tournament round to start after a set time interval, marking it as scheduled
    and setting a start time. It then initializes a timer to check readiness or eliminate participants.

    Args:
        round (TournamentRound): The round to be scheduled.
    """
    round.status = 'scheduled'
    start_time = round.start_time = timezone.now() + timezone.timedelta(seconds=15)
    round.save()
    run_async_task_in_thread(start_round_timer, start_time, round.id)
    print(f"Round {round.number} of tournament {round.tournament.id} is scheduled to start at {start_time}.")


def start_async_task(task):
    """
    Executes an asynchronous task within its own new event loop in a separate thread,
    ensuring the asynchronous code executes independently of the synchronous Django view.

    Args:
        task (callable): The asynchronous task function to execute.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(task())
    loop.close()


def run_async_task_in_thread(func, *args):
    """
    Wraps an asynchronous function call with its arguments into a synchronous function that
    is then run in a separate thread, allowing asynchronous tasks to be initiated from synchronous contexts.

    Args:
        func (callable): The asynchronous function to be executed.
        *args: Arguments to pass to the async function.
    """
    task = partial(func, *args)  # Bind the arguments to the function
    thread = Thread(target=lambda: start_async_task(task))  # Use lambda to call start_async_task with task
    thread.start()


async def start_round_timer(start_time, round_id):
    """
    Waits until a specified start time is reached to perform checks on participants' readiness
    in a tournament round, potentially eliminating unready participants.

    Args:
        start_time (datetime): The scheduled start time for the round.
        round_id (int): The ID of the round to check.
    """

    sleep_seconds = max(0, (start_time - timezone.now()).total_seconds())
    await asyncio.sleep(sleep_seconds)
    print("Round timer has expired.")
    matches = await eliminate_not_ready_players(round_id)
    for match in matches:
        await eliminate_both_players(match)


@database_sync_to_async
def eliminate_not_ready_players(round_id):
    """
    Identifies and processes matches within a round to eliminate participants who are not ready
    by the round's start time, marking their matches accordingly or determining a winner if applicable.

    Args:
        round_id (int): The ID of the round for which to check participant readiness.

    Returns:
        list: A list of matches where actions were taken due to participants not being ready.
    """

    print(f"Checking if all participants are ready for round {round_id}...")
    matches_to_eliminate = []
    try:
        round = TournamentRound.objects.get(id=round_id)
        if round.status != 'scheduled':
            return []
        round.status = 'in progress'
        round.save()
        with transaction.atomic():
            for match in round.matches.all():
                if all(participant.is_ready for participant in match.participants.all()):
                    continue
                if all(not participant.is_ready for participant in match.participants.all()):
                    print(f"All participants in match {match.id} are not ready. Eliminating them from the tournament.")
                    matches_to_eliminate.append(match)
                else:
                    match.winner = match.participants.get(is_ready=True).player
                    match.status = 'completed'
                    match.save()
                    print(f"Match {match.id} has been completed.")
    except TournamentRound.DoesNotExist:
        print(f"Error: Round {round_id} does not exist.")
    return matches_to_eliminate


@database_sync_to_async
def eliminate_both_players(match):
    """
    Marks both participants of a match as eliminated if neither was ready by the round's start time,
    affecting their status in the tournament and the match's outcome.

    Args:
        match (TournamentMatch): The match to process.
    """

    tournament = match.round.tournament

    for participant in match.participants.all():
        try:
            if participant.player:
                tournament_participant = TournamentParticipant.objects.get(tournament=tournament,
                                                                           user=participant.player)
                tournament_participant.status = 'eliminated'
                tournament_participant.save()
                participant.player.tournament_id = None
                participant.player.save()
        except TournamentParticipant.DoesNotExist:
            print(f"Error: TournamentParticipant not found for user {participant.player.username} "
                  f"in tournament {tournament.name}.")

    match.status = 'completed'
    match.save()
    print(f"Match {match.id} has been completed.")


@receiver(post_save, sender=GameSession)
def handle_game_session_finish(sender, instance, **kwargs):
    """
    Handles the finish of a game session by updating the corresponding tournament match,
    marking it as completed and setting the winner.

    Args:
        sender (Model class): The model class of the sender.
        instance (GameSession): The instance of the GameSession that was saved.
        **kwargs: Extra keyword arguments.
    """

    if instance.status == 'finished':
        try:
            match = TournamentMatch.objects.get(game_session_id=instance.id)
            match.status = 'completed'
            match.winner = instance.winner
            match.save()
            print(f"Match {match.id} has been completed.")
        except TournamentMatch.DoesNotExist:
            print("No corresponding TournamentMatch found for the GameSession.")


@receiver(post_save, sender=TournamentMatch)
def handle_match_completion(sender, instance, **kwargs):
    """
    Handles the completion of a tournament match. It progresses the tournament
    and broadcasts a message to update participants about the tournament's progress.

    Args:
        sender (Model class): The model class of the sender.
        instance (TournamentMatch): The instance of the TournamentMatch that was saved.
        **kwargs: Extra keyword arguments.
    """

    if instance.status == 'completed':
        progress_tournament(instance)
        group_name = f"tournament_{instance.round.tournament.id}"
        message_data = {
            'type': 'tournament_message',
            'message': f"Tournament {instance.round.tournament.name} has been updated."
        }
        run_async_task_in_thread(broadcast_message, group_name, message_data)


def progress_tournament(match):
    """
    Processes the progression of the tournament after a match completes. This includes
    eliminating the loser, advancing the winner, and progressing the round.

    Args:
        match (TournamentMatch): The match that has just been completed.
    """

    eliminate_loser(match)
    advance_winner(match)
    round_progress(match.round)


User = get_user_model()
@receiver(post_save, sender=User)
def user_post_save(sender, instance, **kwargs):
    """
    Signal to log when a User instance is saved, specifically looking for changes to the tournament_id field.
    """
    # Log the current state of the tournament_id for the user instance that was saved
    print(f"Post-save signal for {instance.username}: tournament_id is now {instance.tournament_id}")


@transaction.atomic
def eliminate_loser(match):
    """
    Eliminates the loser of a match from the tournament, updating both the match and
    participant records accordingly. Wrapped in a transaction to ensure atomicity.

    Args:
        match (TournamentMatch): The match whose loser needs to be eliminated.
    """
    losers = match.participants.exclude(player=match.winner).all()
    for loser in losers:
        loser_user = loser.player
        if not loser_user:
            continue

        # Attempt to update tournament_id to None
        loser_user.tournament_id = None
        loser_user.save(update_fields=['tournament_id'])
        print(f"{loser_user.username}'s tournament ID updated to {loser_user.tournament_id}.")

        tournament = match.round.tournament
        try:
            tournament_participant = TournamentParticipant.objects.get(
                tournament=tournament,
                user=loser_user
            )
            tournament_participant.status = 'eliminated'
            tournament_participant.save()
            print(f"{loser_user.username} has been eliminated from the tournament.")
        except TournamentParticipant.DoesNotExist:
            print(f"TournamentParticipant not found for user {loser_user.username} in tournament {tournament.name}.")
            
        run_async_task_in_thread(broadcast_message, f"tournament_{tournament.id}", 
                                 {'type': 'tournament_message',
                                  'message': f"{loser_user.username} has been eliminated from the tournament."})
        run_async_task_in_thread(broadcast_message, loser_user.username, {'type': "leave_message"})


def advance_winner(match):
    """
    Advances the winner of a match to their next match in the tournament or marks the tournament as completed
    if the match was the final one.

    Args:
        match (TournamentMatch): The match that has just been completed.
    """

    tournament = match.round.tournament

    if match.round == tournament.rounds.last():
        complete_tournament(tournament, match)
    else:
        place_winner_in_next_round(match, tournament)


def complete_tournament(tournament, match):
    """
    Marks the tournament as completed and updates the status of the winning participant.

    Args:
        tournament (Tournament): The tournament to be marked as completed.
        match (TournamentMatch): The final match of the tournament containing the winner.
    """
    tournament.status = 'completed'
    tournament.save()

    if match.winner:
        match.winner.tournament_id = None
        match.winner.save()
        tournament.winner = match.winner
        tournament.save()
        run_async_task_in_thread(broadcast_message, f"tournament_{tournament.id}", 
                                 {'type': 'tournament_message',
                                  'message': f"{match.winner.username} has won the tournament !"})
        run_async_task_in_thread(broadcast_message, match.winner.username, {'type': "leave_message"})

    participants_string_array = get_participants_string_array(tournament)
    run_async_task_in_thread(set_tournament_in_blockchain,tournament, participants_string_array)

    print(f"Tournament {tournament.id} has been completed.")

def get_participants_string_array(tournament):
    participants_string_array = []

    for participant in tournament.participants.all():
        participants_string_array.append(participant.user.username)

    # To handle empty slots after both player fail the ready check in a match
    participants_string_array.append("None")

    return participants_string_array




def place_winner_in_next_round(match, tournament):
    """
    Places the winner of a match into the next scheduled match in the tournament.

    Args:
        match (TournamentMatch): The match whose winner is to be advanced.
        tournament (Tournament): The tournament containing the match and its subsequent rounds.
    """
    try:
        next_round = tournament.rounds.get(number=match.round.number + 1)
        next_match_number = (match.number + 1) // 2
        next_match = next_round.matches.get(number=next_match_number)
        participant = next_match.participants.filter(player=None).first()
        participant.player = match.winner
        participant.save()
        print(f"Round {match.round.number}: Winner of match {match.number} has been placed in match {next_match_number}\
              of Round {next_round.number}.")
    except TournamentRound.DoesNotExist:
        print(f"Error: Next round does not exist for round number {match.round.number + 1}.")
    except TournamentMatch.DoesNotExist:
        print(f"Error: Match number {next_match_number} in round {match.round.number + 1} does not exist.")
    except MatchParticipant.DoesNotExist:
        print(f"Error: No participant placeholder found for match number {next_match_number} in round \
        {match.round.number + 1}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def round_progress(round):
    """
    Marks a round as completed if all matches within the round are completed, and prepares the tournament
    for the next round.

    Args:
        round (TournamentRound): The round to check and update the status of.
    """
    if all(match.status == 'completed' for match in round.matches.all()):
        round.status = 'completed'
        round.save()
        print(f"Round {round.number} of tournament {round.tournament.id} has been completed.")

        setup_next_round(round)


def setup_next_round(round):
    """
    Schedules the next round in the tournament, updating the statuses of the matches to scheduled.

    Args:
        round (TournamentRound): The round that has just been completed.
    """
    try:
        if round != round.tournament.rounds.last():
            next_round = round.tournament.rounds.get(number=round.number + 1)
            schedule_round(next_round)
            print(f"Round {next_round.number} of tournament {round.tournament.id} is now scheduled.")
            for match in next_round.matches.all():
                match.status = "scheduled"
                match.save()

    except TournamentRound.DoesNotExist:
        print(f"No next round exists for round number {round.number + 1} in tournament {round.tournament.id}.")
