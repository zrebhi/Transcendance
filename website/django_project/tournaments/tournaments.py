from .models import TournamentParticipant, TournamentRound, TournamentMatch, MatchParticipant
from matchmaking.models import GameSession
from django.db import transaction, IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
import random


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
            tournament_round = TournamentRound.objects.create(
                tournament=tournament,
                number=round_number,
                status='scheduled'
            )
            create_matches_for_round(tournament_round, participants, round_number)


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


@receiver(post_save, sender=GameSession)
def handle_game_session_finish(sender, instance, **kwargs):
    # It's important to update the status of the game last
    if instance.status == 'finished':
        try:
            match = TournamentMatch.objects.get(game_session_id=instance.id)
            match.status = 'completed'
            match.winner = instance.winner
            match.save()
            print(f"Match {match.id} has been completed.")
            progress_tournament(match)
        except TournamentMatch.DoesNotExist:
            print("No corresponding TournamentMatch found for the GameSession.")


def progress_tournament(match):
    eliminate_loser(match)
    advance_winner(match)
    round_progress(match.round)


def eliminate_loser(match):
    for participant in match.participants.all():
        if participant.player != match.winner:
            participant.status = 'eliminated'
            participant.save()


def advance_winner(match):
    tournament = match.round.tournament

    if match.round == tournament.rounds.last():
        complete_tournament(tournament)
    else:
        place_winner_in_next_round(match, tournament)


def complete_tournament(tournament):
    tournament.status = 'completed'
    tournament.save()
    for participant in tournament.participants.all():
        participant.user.tournament_id = None
        participant.save()
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
            next_round.status = 'scheduled'
            next_round.save()
            print(f"Round {next_round.number} of tournament {round.tournament.id} is now scheduled.")
            for match in next_round.matches.all():
                match.status = "scheduled"
                match.save()

    except TournamentRound.DoesNotExist:
        print(f"No next round exists for round number {round.number + 1} in tournament {round.tournament.id}.")

