# pong_app/urls.py

from django.urls import path
from .views import game_view

urlpatterns = [
    path('', game_view, name='frontend'),
    # Add more URL patterns if needed
]
