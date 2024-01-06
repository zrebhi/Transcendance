from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
def main_view(request):
    return render(request, 'main_template.html')

def home_view(request):
    html = render_to_string('home_template.html')
    return HttpResponse(html)

from django.shortcuts import render

def navbar_view(request):
    return render(request, 'navbar.html')

def sidebar_view(request):
    return render(request, 'sidebar.html')


