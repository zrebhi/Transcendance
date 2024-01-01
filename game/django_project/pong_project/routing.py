# routing.py

from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from pong_app.consumers import GameConsumer

websocket_urlpatterns = [
    re_path("ws/socket-server/", GameConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
})
