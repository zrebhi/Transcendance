from django.db import models
from django.contrib.auth.models import User

class QueueEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_connected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} joined at {self.joined_at}"


class GameSession(models.Model):
    player1 = models.ForeignKey(User, related_name='game_session_as_player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(User, related_name='game_session_as_player2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # Add other fields as needed, such as game status, scores, etc.

    def __str__(self):
        return f"Game between {self.player1.username} and {self.player2.username} started at {self.created_at}"
