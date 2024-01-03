from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import render

def game_view(request):
    html = render_to_string('pong_template.html')
    return HttpResponse(html)
    # return render(request, 'pong_template.html')

