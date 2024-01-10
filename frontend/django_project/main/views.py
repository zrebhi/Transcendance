from django.shortcuts import render

def main_view(request):
    return render(request, 'main_template.html')

def home_view(request):
    return render(request, 'home_template.html')

def navbar_view(request):
    return render(request, 'navbar.html')

def sidebar_view(request):
    return render(request, 'sidebar.html')

def queue_view(request):
    return render(request, 'queue.html')