# Generated by Django 5.0.1 on 2024-02-21 14:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0006_alter_gamesession_mode_alter_gamesession_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='gamesession',
            name='winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='game_session_winner', to=settings.AUTH_USER_MODEL),
        ),
    ]