# Generated by Django 5.0.1 on 2024-01-15 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0003_gamesession_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamesession',
            name='status',
            field=models.CharField(default='pending', max_length=20),
        ),
    ]
