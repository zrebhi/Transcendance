from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/game/<int:game_session_id>/', consumers.GameConsumer.as_asgi()),
]
