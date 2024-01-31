from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from users.models import CustomUser

User = get_user_model()


class Tournament(models.Model):
    name = models.CharField(max_length=100, blank=True)  # Allow blank names initially
    status = models.CharField(max_length=15, choices=[('open', 'Open'), ('in progress', 'In Progress'),
                                                      ('completed', 'Completed')], default='open')
    creator: 'CustomUser' = models.ForeignKey(User, related_name='creator', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Set default name if not provided
        if not self.name:
            self.name = f"{self.creator.username}'s Tournament"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.status}"


class TournamentParticipant(models.Model):
    tournament = models.ForeignKey(Tournament, related_name='participants', on_delete=models.CASCADE)
    user: 'CustomUser' = models.ForeignKey(User, related_name='tournament_participations', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('eliminated', 'Eliminated')])

    class Meta:
        # Ensures that a user can only participate in a tournament once
        unique_together = ('tournament', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.tournament.name}"
