from django.db import IntegrityError, transaction
from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import TournamentParticipant, Tournament
from .forms import TournamentCreationForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


def tournament_list(request):
    tournaments = Tournament.objects.filter(status="open")
    return render(request, 'tournaments_list.html', {'tournaments': tournaments})


def tournament_view(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    return render(request, 'custom_tournament.html', {'tournament': tournament})


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

    return render(request, 'create_tournament.html', {'form': form})


@login_required
@require_POST
def join_tournament(request, tournament_id):
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Tournament not found'}, status=404)

    if add_participant_to_tournament(tournament, request.user):
        request.user.tournament_id = tournament.id
        return JsonResponse({'success': True, 'message': 'Successfully joined the tournament',
                             'next_url': f'/tournaments/{tournament.id}'})
    else:
        if tournament.participants.count() >= 8:
            return JsonResponse({'success': False, 'message': 'Tournament is already full'}, status=400)
        return JsonResponse({'success': False,
                             'message': 'Could not join the tournament. You may already be registered.'}, status=400)


def add_participant_to_tournament(tournament, user):
    if tournament.participants.count() < 8:
        try:
            with transaction.atomic():
                # Ensures that if any of the database operations fail, none of them will be executed.
                TournamentParticipant.objects.create(tournament=tournament, user=user)
                user.tournament_id = tournament.id
                user.save()
            return True
        except IntegrityError:
            # This happens if the user is already registered in the tournament.
            # Comes from the unique_together in the TournamentParticipant model.
            return False
    else:
        # Tournament is full
        return False
