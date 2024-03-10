from users.models import CustomUser
from tournaments.models import Tournament, TournamentMatch, TournamentRound


def clear_session_ids():
    for user in CustomUser.objects.all():
        user.session_id = None
        user.save()


def clear_tournament_ids():
    for user in CustomUser.objects.all():
        user.tournament_id = None
        user.save()


def clear_tournaments():
    Tournament.objects.all().delete()


def reset_tournament(tournament):
    tournament.status = 'in progress'
    tournament.save()
    print(f"Tournament {tournament.name} has been reset to in progress.")
    first_round_number = tournament.rounds.first().number if tournament.rounds.exists() else None
    for round in tournament.rounds.all():
        round.status = 'scheduled' if round.number == first_round_number else 'created'
        round.save()
        print(f"Round {round.number} has been reset to {round.status}.")
        for match in round.matches.all():
            for participant in match.participants.all():
                participant.is_ready = False
                if round.status != 'scheduled':
                    participant.player = None
                participant.save()
            match.status = round.status
            match.winner = None
            match.save()
            print(f"Match {match.number} in round {round.number} has been reset to {match.status}, participants updated.")


def display_tournament_progress(tournament):
    print(f"Tournament: {tournament.name}, Status: {tournament.status}")
    for round in tournament.rounds.all().order_by('number'):
        print(f"  Round {round.number}, Status: {round.status}")
        for match in round.matches.all().order_by('number'):
            participants = match.participants.all()
            participant_names = []
            for participant in participants:
                if participant.player:
                    participant_name = (f"{participant.player.username} (Ready: {'Yes' if participant.is_ready else 'No'}) Status: {participant.status}")
                else:
                    participant_name = "TBD (To Be Determined)"
                participant_names.append(participant_name)
            winner_name = match.winner.username if match.winner else 'N/A'
            print(f"    Match {match.number}, Status: {match.status}, Winner: {winner_name}")
            print(f"      Participants: {', '.join(participant_names)}")


admin = CustomUser.objects.get(username='admin')
Zak = CustomUser.objects.get(username='Zak')
Zak2 = CustomUser.objects.get(username='Zak2')
Zak3 = CustomUser.objects.get(username='Zak3')
