from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from pong_app.routing import websocket_urlpatterns as pong_websocket_urlpatterns
from matchmaking.routing import websocket_urlpatterns as matchmaking_websocket_urlpatterns
from tournaments.routing import websocket_urlpatterns as tournaments_websocket_urlpatterns

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": get_asgi_application(),

    # Django Channels routing for websocket
    "websocket": AuthMiddlewareStack(
        URLRouter(
            pong_websocket_urlpatterns + matchmaking_websocket_urlpatterns + tournaments_websocket_urlpatterns
        )
    ),
})
