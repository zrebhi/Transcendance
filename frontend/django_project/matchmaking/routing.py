from django.urls import path
from matchmaking.consumers import QueueConsumer

websocket_urlpatterns = [
    path('ws/queue/', QueueConsumer.as_asgi()),  # Define the path for QueueConsumer
]
