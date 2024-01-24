from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_view, name='main_view'),
    path('home/', views.home_view, name='home_view'),
    path('navbar/', views.navbar_view, name='navbar_view'),
    path('sidebar/', views.sidebar_view, name='sidebar_view'),
    path('queue/', views.queue_view, name='queue_view'),
]
