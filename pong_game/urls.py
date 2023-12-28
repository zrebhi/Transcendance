# pong_game/urls.py

from django.urls import path
from .views import pong_game_view

urlpatterns = [
    path('pong/', pong_game_view, name='pong_game'),
    # Add more URL patterns if needed
]
