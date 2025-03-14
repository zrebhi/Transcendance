from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register_view'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('profile/', views.user_profile_view, name='user_profile_view'),
    path('change-alias/', views.update_alias_user, name="update_alias_user"),
]
