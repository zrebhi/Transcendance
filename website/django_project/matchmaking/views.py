from django.http import JsonResponse
from .models import QueueEntry, GameSession
from django.views.decorators.http import require_http_methods
from pong_app.consumers import create_game_instance


@require_http_methods(["POST"])
def join_queue(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)

    if QueueEntry.objects.filter(user=request.user).exists():
        return JsonResponse({'status': 'error', 'message': 'User already in queue'}, status=400)

    if request.user.session_id is not None:
        return JsonResponse({'status': 'error', 'message': 'User already in a game'}, status=400)

    QueueEntry.objects.create(user=request.user)

    return JsonResponse({'status': 'success', 'message': 'Successfully joined the queue'})


def local_game(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=400)
    if request.user.session_id is not None:
        return JsonResponse({'status': 'error', 'message': 'User already in a game'}, status=400)

    session = GameSession.objects.create(player1=request.user, player2=request.user, mode='local')
    create_game_instance(session.id)
    request.user.session_id = session.id
    request.user.save()
    return JsonResponse({'status': 'success', 'message': 'Successfully created a local game', 'session_id': session.id})


