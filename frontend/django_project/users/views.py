from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.http import HttpResponse
from django.http import JsonResponse
from django.template.loader import render_to_string


def register(request):
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



