from django.contrib import admin
from .models import QueueEntry, GameSession

# Register your models here.
admin.site.register(QueueEntry)
admin.site.register(GameSession)
