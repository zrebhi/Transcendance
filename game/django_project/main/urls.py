from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_view, name='main_view'),
    path('home/', views.home_view, name='home_view')
]
