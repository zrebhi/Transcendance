# Generated by Django 5.0.1 on 2024-03-04 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0009_tournamentmatch_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournamentround',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tournamentparticipant',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('eliminated', 'Eliminated')], default='active', max_length=50),
        ),
    ]
