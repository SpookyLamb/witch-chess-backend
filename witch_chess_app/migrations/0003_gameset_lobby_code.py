# Generated by Django 5.0.6 on 2024-06-12 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('witch_chess_app', '0002_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameset',
            name='lobby_code',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]