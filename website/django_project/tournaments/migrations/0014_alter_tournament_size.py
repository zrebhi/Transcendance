# Generated by Django 5.0.6 on 2024-05-14 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0013_remove_tournamentparticipant_tournament_nickname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='size',
            field=models.IntegerField(default=4),
        ),
    ]
