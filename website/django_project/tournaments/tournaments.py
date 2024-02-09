from .models import TournamentParticipant, TournamentRound, TournamentMatch, MatchParticipant
from django.db import transaction, IntegrityError
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
                status=match_status
            )

            # For the first round, we can pair the participants directly
            # For subsequent rounds, we don't know the participants yet
            players = [participants[i * 2].user, participants[i * 2 + 1].user] if round_number == 1 else [None, None]
            MatchParticipant.objects.create(match=match, player=players[0], is_ready=False)
            MatchParticipant.objects.create(match=match, player=players[1], is_ready=False)
