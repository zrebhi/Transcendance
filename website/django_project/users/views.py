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

@login_required
def update_alias_user(request):

    if request.user.tournament_id is not None:
        return JsonResponse({'success': False, 'message': 'User already in a tournament', 'form_html': '<div><p>User already in a tournament</p></div>'})

    if request.method == "POST":
        new_alias = request.POST.get('alias', 'default').strip()

        if not new_alias:
            return JsonResponse({'success': False, 'message': 'Invalid or empty alias', 'form_html': '<div><p>Invalid or empty alias</p></div>'})

        if len(new_alias) > 10:
            return JsonResponse({'success': False, 'message': 'Alias must be 10 characters or less', 'form_html': '<div><p>Alias must be 10 characters or less</p></div>'})
        
        request.user.alias = new_alias
        request.user.save()

        return JsonResponse({'success': True, 'message': 'Alias updated successfully', 'next_url': '/home/'})
    
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request'})

