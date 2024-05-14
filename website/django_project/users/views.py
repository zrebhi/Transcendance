import re
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .forms import CustomUserCreationForm, CustomLoginForm
from main.utils import render_template

def register_view(request):
    """
    Handle user registration. If the request is POST, process the form data
    to register a new user. If the request is GET, display the registration form.
    """
    if request.user.is_authenticated:
        return render_template(request, 'home_template.html')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return JsonResponse({'success': True, 'next_url': '/home/'})
        else:
            form_html = render_to_string('register_en.html', {'form': form}, request=request)
            return JsonResponse({'success': False, 'form_html': form_html})
    else:
        form = CustomUserCreationForm()

    return render_template(request, 'register.html', {'form': form})


def login_view(request):
    """
    Handle user login. On POST, validate the form and authenticate the user.
    If valid, log in the user and redirect. For GET requests, show the login form.
    """
    if request.user.is_authenticated:
        return render_template(request, 'home_template.html')

    next_url = request.GET.get('next', '/home/')

    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'next_url': next_url})
            else:
                form.add_error(None, 'Invalid username or password')
        form_html = render_to_string('login_en.html', {'form': form}, request=request)
        return JsonResponse({'success': False, 'form_html': form_html})
    else:
        form = CustomLoginForm()

    return render_template(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    """
    Handle the user logout process. This includes logging out the user and
    closing any active WebSocket connections associated with their session.
    """

    channel_layer = get_channel_layer()
    channel_names = request.session.pop('channel_names', [])
    for channel_name in channel_names:
        async_to_sync(channel_layer.send)(
            channel_name,
            {'type': 'leave_message'}
        )
        print(f"logout message sent to {channel_name}")

    logout(request)
    return JsonResponse({'success': True, 'next_url': '/home/'})

@login_required
def user_profile_view(request):
    return render_template(request, 'user_profile.html')

@login_required
def get_user_session(request):
    return JsonResponse({'session_id': request.user.session_id})

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import re

@login_required
def update_alias_user(request):
    if request.method == "POST":
        language = request.POST.get('lang', 'en')

        if language == 'es':
            already_in_tournament = 'Usuario ya en un torneo'
            invalid_alias = 'Alias inválido o vacío'
            alias_must_contain = 'El alias debe contener solo letras y números'
            alias_must_be_10 = 'El alias debe tener 10 caracteres o menos'
        elif language == 'fr':
            already_in_tournament = 'Utilisateur déjà dans un tournoi'
            invalid_alias = 'Alias invalide ou vide'
            alias_must_contain = 'L\'alias ne doit contenir que des lettres et des chiffres'
            alias_must_be_10 = 'L\'alias doit comporter 10 caractères ou moins'
        else:
            already_in_tournament = 'User already in a tournament'
            invalid_alias = 'Invalid or empty alias'
            alias_must_contain = 'Alias must contain only letters and numbers'
            alias_must_be_10 = 'Alias must be 10 characters or less'

        if request.user.tournament_id is not None:
            return JsonResponse({'success': False, 'message': already_in_tournament, 'form_html': f'<div><p>{already_in_tournament}</p></div>'})

        new_alias = request.POST.get('alias', 'default').strip()

        if not new_alias:
            return JsonResponse({'success': False, 'message': invalid_alias, 'form_html': f'<div><p>{invalid_alias}</p></div>'})

        if not re.match("^[a-zA-Z0-9]*$", new_alias):
            return JsonResponse({'success': False, 'message': alias_must_contain, 'form_html': f'<div><p>{alias_must_contain}</p></div>'})

        if len(new_alias) > 20:
            return JsonResponse({'success': False, 'message': alias_must_be_10, 'form_html': f'<div><p>{alias_must_be_10}</p></div>'})

        request.user.alias = new_alias
        request.user.save()

        return JsonResponse({'success': True, 'message': 'Alias updated successfully', 'next_url': '/tournaments/'})

    else:
        return JsonResponse({'success': False, 'message': 'Invalid request'})
