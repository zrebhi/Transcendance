from django.http import JsonResponse
from .models import QueueEntry
from django.views.decorators.http import require_http_methods

@require_http_methods(["POST"])
def join_queue(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)

    if QueueEntry.objects.filter(user=request.user).exists():
        return JsonResponse({'status': 'error', 'message': 'User already in queue'}, status=400)

    QueueEntry.objects.create(user=request.user)

    return JsonResponse({'status': 'success', 'message': 'Successfully joined the queue'})
