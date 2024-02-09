from users.models import CustomUser
from tournaments.models import Tournament


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
