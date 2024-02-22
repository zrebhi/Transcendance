from django.db import models
from django.contrib.auth import get_user_model
from typing import TYPE_CHECKING
from matchmaking.models import GameSession

if TYPE_CHECKING:
    from users.models import CustomUser

User = get_user_model()


class Tournament(models.Model):
    name = models.CharField(max_length=50, blank=True)  # Allow blank names initially
    status = models.CharField(max_length=15, choices=[('open', 'Open'), ('in progress', 'In Progress'),
                                                      ('completed', 'Completed')], default='open')
    creator: 'CustomUser' = models.ForeignKey(User, related_name='creator', on_delete=models.CASCADE)
    size = models.IntegerField(default=8)

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


class TournamentRound(models.Model):
    tournament = models.ForeignKey(Tournament, related_name='rounds', on_delete=models.CASCADE)
    number = models.IntegerField()
    status = models.CharField(max_length=20, choices=[('scheduled', 'Scheduled'), ('in progress', 'In Progress'),
                                                      ('completed', 'Completed')], default='scheduled')

    class Meta:
        unique_together = ('tournament', 'number')
        ordering = ['number']

    def __str__(self):
        return f"Round {self.number} of {self.tournament.name}"


class TournamentMatch(models.Model):
    round = models.ForeignKey(TournamentRound, related_name='matches', on_delete=models.CASCADE)
    game_session = models.OneToOneField(GameSession, related_name='tournament_match', on_delete=models.CASCADE,
                                        null=True, blank=True)
    status = models.CharField(choices=[('created', 'Created'), ('scheduled', 'Scheduled'),
                                       ('in progress', 'In Progress'), ('completed', 'Completed')], default='created',
                              max_length=20)
    winner = models.ForeignKey(User, related_name='won_tournament_matches', on_delete=models.SET_NULL,
                               null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        participants = self.participants.all()
        players = [participant.player.username for participant in participants]
        return f"Match in {self.round} between {' and '.join(players)}"


class MatchParticipant(models.Model):
    match = models.ForeignKey(TournamentMatch, related_name='participants', on_delete=models.CASCADE,
                              null=True, blank=True)
    player: 'CustomUser' = models.ForeignKey(User, related_name='match_participations', on_delete=models.CASCADE,
                                             null=True, blank=True)
    is_ready = models.BooleanField(default=False)

    class Meta:
        unique_together = ('match', 'player')

    def __str__(self):
        return f"{self.player.username} in {self.match} - {'Ready' if self.is_ready else 'Not Ready'}"
