from django.shortcuts import render
from users.models import CustomUser
from django.contrib.auth import get_user
from pong_project.utils import render_template

def main_view(request):
    return render_template(request, 'main_template.html')

def home_view(request):
    return render_template(request, 'home_template.html')

def navbar_view(request):
    user = get_user(request)
    return render_template(request, 'navbar.html', {'user': user})


def sidebar_view(request):
    user = get_user(request)
    return render_template(request, 'sidebar.html', {'user': user})

def queue_view(request):
    return render_template(request, 'queue.html')