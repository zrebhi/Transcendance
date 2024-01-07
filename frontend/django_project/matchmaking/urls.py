from django.urls import path
from .views import join_queue

urlpatterns = [
    path('', join_queue, name='join_queue'),
]