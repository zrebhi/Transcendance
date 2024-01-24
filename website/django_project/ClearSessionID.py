from users.models import CustomUser

def clear_session_id():
    for user in CustomUser.objects.all():
        user.session_id = None
        user.save()