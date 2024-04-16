from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from pong_app.consumers import broadcast_message
from main.utils import render_template
from .models import Tournament, TournamentParticipant, TournamentMatch
from .forms import TournamentCreationForm
from .tournaments import add_participant_to_tournament, start_tournament, run_async_task_in_thread

@login_required
def tournament_list(request):
    tournaments = Tournament.objects.all()
    return render_template(request, 'tournaments_list.html', {'tournaments': tournaments})

@login_required
def tournament_view(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    user = request.user

    participant = None

    for _round in tournament.rounds.all():
        for match in _round.matches.all():
            if match.participants.filter(player=user).exists() and match.status != 'completed':
                participant = match.participants.get(player=user)
                break
        if participant:
            break

    context = {
        'tournament': tournament,
        'participant': participant,
    }

    return render_template(request, 'tournament.html', context)


@login_required
def create_tournament(request):
    """
    Handle tournament creation. On POST, validate the form and create a tournament.
    For GET requests, display the tournament creation form.
    """
    if request.method == 'POST':
        form = TournamentCreationForm(data=request.POST, creator=request.user)
        if form.is_valid():
            # Create the tournament but don't commit to the database yet so that we can add the creator
            tournament = form.save(commit=False)
            tournament.creator = request.user
            tournament.save()
            add_participant_to_tournament(tournament, request.user)

            return JsonResponse({'success': True, 'next_url': f'/tournaments/{tournament.id}'})

        # If the form is not valid, render it again with errors
        form_html = render_to_string('create_tournament.html', {'form': form}, request=request)
        return JsonResponse({'success': False, 'form_html': form_html})

    else:
        # For a GET request, just display the blank form
        form = TournamentCreationForm(creator=request.user)

    return render_template(request, 'create_tournament.html', {'form': form})


@login_required
@require_POST
def join_tournament(request, tournament_id):
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Tournament not found'}, status=404)

    if add_participant_to_tournament(tournament, request.user):
        request.user.tournament_id = tournament.id
        if tournament.participants.count() == tournament.size:
            start_tournament(tournament)
        return JsonResponse({'success': True, 'message': 'Successfully joined the tournament',
                             'next_url': f'/tournaments/{tournament.id}'})
    else:
        if tournament.participants.count() >= tournament.size:
            return JsonResponse({'success': False, 'message': 'Tournament is already full'}, status=400)
        return JsonResponse({'success': False,
                             'message': 'Could not join the tournament. You may already be registered.'}, status=401)

@login_required
@require_POST
def leave_tournament(request, tournament_id):
    try:
        tournament = Tournament.objects.get(id=tournament_id)
        participant = TournamentParticipant.objects.get(tournament=tournament, user=request.user)
        participant.delete()
        request.user.tournament_id = None
        request.user.save()
        # Broadcast a message indicating the user has left the tournament
        run_async_task_in_thread(broadcast_message, f"tournament_{tournament.id}",
                                 {'type': 'tournament_message',
                                  'message': f"{request.user.username} has left the tournament."})
        if not TournamentParticipant.objects.filter(tournament=tournament).exists():
            tournament.delete()
        return JsonResponse({'success': True, 'message': 'Successfully left the tournament'})
    except Tournament.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Tournament not found'}, status=404)
    except TournamentParticipant.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'You are not a participant in this tournament'}, status=402)
        