from django.urls import path
from .views import join_queue, local_game

urlpatterns = [
    path('', join_queue, name='join_queue'),
    path('local_game/', local_game, name='local_game'),
]