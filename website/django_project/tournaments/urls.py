from django.urls import path
from .views import tournaments_view, create_tournament, join_tournament

urlpatterns = [
    path('', tournaments_view, name='tournaments_view'),
    path('create/', create_tournament, name='create_tournament'),
    path('join/<int:tournament_id>/', join_tournament, name='join_tournament')
]