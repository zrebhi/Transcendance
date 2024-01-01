# pong_app/urls.py

from django.urls import path
from .views import pong_game_view

urlpatterns = [
    path('pong/', pong_game_view, name='pong_app'),
    # Add more URL patterns if needed
]
