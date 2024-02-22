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
