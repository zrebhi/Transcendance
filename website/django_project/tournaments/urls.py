from django.urls import path
from .views import tournament_list, create_tournament, join_tournament, tournament_view

urlpatterns = [
    path('', tournament_list, name='tournaments_view'),
    path('create/', create_tournament, name='create_tournament'),
    path('join/<int:tournament_id>/', join_tournament, name='join_tournament'),
    path('<int:tournament_id>/', tournament_view, name='tournament_view'),
]
