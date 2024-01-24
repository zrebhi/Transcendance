from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from users.models import CustomUser


class QueueEntry(models.Model):
    user: 'CustomUser' = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} joined at {self.joined_at}"


class GameSession(models.Model):
    User = get_user_model()

    player1: 'CustomUser' = models.ForeignKey(User, related_name='game_session_as_player1', on_delete=models.CASCADE)
    player2: 'CustomUser' = models.ForeignKey(User, related_name='game_session_as_player2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    mode = models.CharField(max_length=20, null=True)

    def __str__(self):
        return (f"Game between {self.player1.username} and {self.player2.username} "
                f"started at {self.created_at}, status: {self.status}")
