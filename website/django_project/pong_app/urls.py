from django.urls import path
from .views import game_view

urlpatterns = [
    path('<int:session_id>/', game_view, name='game_view'),
]

