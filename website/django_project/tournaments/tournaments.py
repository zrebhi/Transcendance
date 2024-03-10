from .models import TournamentParticipant, TournamentRound, TournamentMatch, MatchParticipant
from matchmaking.models import GameSession
from django.db import transaction, IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.db import database_sync_to_async
from django.utils import timezone
from pong_app.consumers import broadcast_message
from threading import Thread
from functools import partial
import asyncio
import random


# tournament_app
# |
# |-- start_tournament(tournament)
# |   |-- create_tournament_rounds_and_matches(tournament)
# |       |-- create_matches_for_round(tournament_round, participants, round_number)
# |
# |-- handle_game_session_finish(sender, instance, **kwargs)
# |   |-- (Triggered by post_save signal of GameSession)
# |   |-- progress_tournament(match)
# |       |-- eliminate_loser(match)
# |       |-- advance_winner(match)
# |           |-- place_winner_in_next_round(match, tournament) (conditional)
# |           |-- complete_tournament(tournament, match) (conditional)
# |       |-- round_progress(match.round)
# |           |-- setup_next_round(round)


def add_participant_to_tournament(tournament, user):
    if tournament.participants.count() < tournament.size:
        try:
            with transaction.atomic():
                # Ensures that if any of the database operations fail, none of them will be executed.
                TournamentParticipant.objects.create(tournament=tournament, user=user)
                user.tournament_id = tournament.id
                user.save()
            return True
        except IntegrityError:
            # This happens if the user is already registered in the tournament.
            # Comes from the unique_together in the TournamentParticipant model.
            return False
    else:
        # Tournament is full
        return False


def start_tournament(tournament):
    if tournament.status == 'open' and tournament.participants.count() == tournament.size:
        # Transition tournament status to "in progress"
        tournament.status = 'in progress'
        tournament.save()
        create_tournament_rounds_and_matches(tournament)


def create_tournament_rounds_and_matches(tournament):
    participants = list(tournament.participants.all())
    total_rounds = 2  # For a 4 participants tournament

    random.shuffle(participants)  # Shuffle the participants to randomize the matches

    with transaction.atomic():
        # Create matches for all rounds
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
    # Number of matches halves each round for a single-elimination tournament
    num_matches = 2 ** (2 - round_number)  # Adjust based on your tournament structure

    with transaction.atomic():
        for i in range(num_matches):
            match_status = 'scheduled' if round_number == 1 else 'created'

            match = TournamentMatch.objects.create(
                round=tournament_round,
                status=match_status,
                number=i + 1
            )

            # For the first round, we can pair the participants directly
            # For subsequent rounds, we don't know the participants yet
            players = [participants[i * 2].user, participants[i * 2 + 1].user] if round_number == 1 else [None, None]
            MatchParticipant.objects.create(match=match, player=players[0], is_ready=False)
            MatchParticipant.objects.create(match=match, player=players[1], is_ready=False)


def schedule_round(round):
    round.status = 'scheduled'
    start_time = round.start_time = timezone.now() + timezone.timedelta(seconds=15)
    round.save()
    run_async_task_in_thread(start_round_timer, start_time, round.id)
    print(f"Round {round.number} of tournament {round.tournament.id} is scheduled to start at {start_time}.")


def start_async_task(task):
    """Function to run the async function in its event loop and run it in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(task())
    loop.close()


def run_async_task_in_thread(func, *args):
    """Function to run the async function in a separate thread."""
    task = partial(func, *args)  # Bind the arguments to the function
    thread = Thread(target=lambda: start_async_task(task))  # Use lambda to call start_async_task with task
    thread.start()


async def start_round_timer(start_time, round_id):
    sleep_seconds = max(0, (start_time - timezone.now()).total_seconds())
    await asyncio.sleep(sleep_seconds)
    print("Round timer has expired.")
    matches = await eliminate_not_ready_players(round_id)
    for match in matches:
        await eliminate_both_players(match)


@database_sync_to_async
def eliminate_not_ready_players(round_id):
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
    if instance.status == 'completed':
        progress_tournament(instance)
        group_name = f"tournament_{instance.round.tournament.id}"
        message_data = {
            'type': 'tournament_message',
            'message': f"Tournament {instance.round.tournament.name} has been updated."
        }
        run_async_task_in_thread(broadcast_message, group_name, message_data)


def progress_tournament(match):
    eliminate_loser(match)
    advance_winner(match)
    round_progress(match.round)


def eliminate_loser(match):
    losers = match.participants.exclude(player=match.winner).all()
    for loser in losers:
        loser_user = loser.player
        if not loser_user:
            continue
        loser_user.tournament_id = None
        loser_user.save()

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


def advance_winner(match):
    tournament = match.round.tournament

    if match.round == tournament.rounds.last():
        complete_tournament(tournament, match)
    else:
        place_winner_in_next_round(match, tournament)


def complete_tournament(tournament, match):
    tournament.status = 'completed'
    tournament.save()

    if match.winner:
        match.winner.tournament_id = None
        match.winner.save()

    print(f"Tournament {tournament.id} has been completed.")


def place_winner_in_next_round(match, tournament):
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
    if all(match.status == 'completed' for match in round.matches.all()):
        round.status = 'completed'
        round.save()
        print(f"Round {round.number} of tournament {round.tournament.id} has been completed.")

        setup_next_round(round)


def setup_next_round(round):
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


@database_sync_to_async
def round_status_is_scheduled(round):
    return round.status == 'scheduled'
