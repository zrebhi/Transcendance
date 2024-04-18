from django.shortcuts import get_object_or_404
from matchmaking.models import GameSession
from pong_project.utils import render_template


def game_view(request, session_id):
    game_session = get_object_or_404(GameSession, id=session_id)
    context = {'game_session': game_session}
    return render_template(request, 'pong_template.html', context)


