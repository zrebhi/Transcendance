from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    session_id = models.IntegerField(null=True, blank=True, default=None)
    tournament_id = models.IntegerField(null=True, blank=True, default=None)
    alias = models.CharField(max_length=20, blank=True, default='')

    def save(self, *args, **kwargs):
        if not self.alias:
            self.alias = self.username[:20]  # Prend les 20 premiers caractères du username
        super(CustomUser, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.alias}'




