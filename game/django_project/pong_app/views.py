from django.shortcuts import render

def pong_game_view(request):
    return render(request, 'pong_template.html')

