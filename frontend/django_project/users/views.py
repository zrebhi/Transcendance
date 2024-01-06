from .forms import CustomUserCreationForm, CustomLoginForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return JsonResponse({'success': True, 'next_url': '/home/'})
        else:
            # Render the form with errors to a string
            form_html = render_to_string('register.html', {'form': form}, request=request)
            return JsonResponse({'success': False, 'form_html': form_html})
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'next_url': '/home/'})
            else:
                # Handle case where authentication fails
                form.add_error(None, 'Invalid username or password')
        # Render the form with errors to a string for AJAX response
        form_html = render_to_string('login.html', {'form': form}, request=request)
        return JsonResponse({'success': False, 'form_html': form_html})
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return JsonResponse({'success': True, 'next_url': '/home/'})


