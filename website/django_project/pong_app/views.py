from django.shortcuts import get_object_or_404
from matchmaking.models import GameSession
from django.shortcuts import render


def game_view(request, session_id):
    game_session = get_object_or_404(GameSession, id=session_id)
    if game_session.status == 'finished':
        return render(request, 'home_template.html')
    context = {'game_session': game_session}
    return render(request, 'pong_template.html', context)


