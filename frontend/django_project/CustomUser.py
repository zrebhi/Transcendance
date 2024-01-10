from django.contrib.auth.models import User
from users.models import CustomUser, OldUser
from django.db import transaction

def copy_users():
    with transaction.atomic():
        for user in OldUser.objects.all():
                CustomUser.objects.create(
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    password=user.password,  # Note: This will copy the password hash
                    is_staff=user.is_staff,
                    is_active=user.is_active,
                    is_superuser=user.is_superuser,
                    last_login=user.last_login,
                    date_joined=user.date_joined,
                    session_id=None
                )
