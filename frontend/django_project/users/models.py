from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    session_id = models.IntegerField(null=True, blank=True, default=None)
    def __str__(self):
        return f'User: {self.username}, ID: {self.session_id}'

class OldUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False  # No database table creation or deletion operations will be performed for this model
        db_table = 'auth_user'  # The name of the table this model should query

    def __str__(self):
        return self.username




