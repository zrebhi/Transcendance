"""
URL configuration for pong_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('main.urls')),
    path('pong/', include('pong_app.urls')),
    path('users/', include('users.urls')),
    path('matchmaking/', include('matchmaking.urls')),
    path('tournaments/', include('tournaments.urls')),

]

if settings.DEBUG:
    urlpatterns += static('main/static/', document_root=settings.MAIN_STATIC_ROOT)
    urlpatterns += static('pong_app/static/', document_root=settings.PONG_STATIC_ROOT)
    urlpatterns += static('users/static/', document_root=settings.USERS_STATIC_ROOT)
    urlpatterns += static('matchmaking/static/', document_root=settings.MATCHMAKING_STATIC_ROOT)
    urlpatterns += static('tournaments/static/', document_root=settings.TOURNAMENTS_STATIC_ROOT)
