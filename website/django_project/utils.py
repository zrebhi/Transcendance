from users.models import CustomUser
from tournaments.models import Tournament, TournamentMatch, TournamentRound


def clear_session_id():
    for user in CustomUser.objects.all():
        user.session_id = None
        user.save()


def clear_tournament_id():
    for user in CustomUser.objects.all():
        user.tournament_id = None
        user.save()


def clear_tournaments():
    Tournament.objects.all().delete()


def reset_tournament_matches():
    for round in TournamentRound.objects.all():
        if round.status == 'scheduled':
            for match in round.matches.all():
                match.status = 'scheduled'
                match.save()


def display_tournament_progress(tournament):
    print(f"Tournament: {tournament.name}, Status: {tournament.status}")

    for round in tournament.rounds.all().order_by('number'):
        print(f"  Round {round.number}, Status: {round.status}")

        for match in round.matches.all().order_by('number'):
            participants = match.participants.all()
            participant_names = []
            for participant in participants:
                if participant.player:
                    participant_name = f"{participant.player.username} (Ready: {'Yes' if participant.is_ready else 'No'})"
                else:
                    participant_name = "TBD (To Be Determined)"
                participant_names.append(participant_name)

            winner_name = match.winner.username if match.winner else 'N/A'
            print(f"    Match {match.number}, Status: {match.status}, Winner: {winner_name}")
            print(f"      Participants: {', '.join(participant_names)}")
