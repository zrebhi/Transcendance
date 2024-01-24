from django.urls import path
from .consumers import TournamentConsumer

websocket_urlpatterns = [
    path('ws/tournament/', TournamentConsumer.as_asgi()),  # Define the path for QueueConsumer
]