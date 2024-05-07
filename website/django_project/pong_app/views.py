from django.shortcuts import get_object_or_404
from matchmaking.models import GameSession
from django.contrib.auth.decorators import login_required
from main.utils import render_template

@login_required
def game_view(request, session_id):
    game_session = get_object_or_404(GameSession, id=session_id)
    if game_session.status == 'finished':
        return render_template(request, 'home_template.html')
    context = {'game_session': game_session}
    return render_template(request, 'pong_template.html', context)
