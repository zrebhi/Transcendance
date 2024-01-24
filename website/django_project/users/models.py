from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    session_id = models.IntegerField(null=True, blank=True, default=None)
    tournament_id = models.IntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return f'{self.username}'




