# Generated by Django 5.0.6 on 2024-06-12 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('witch_chess_app', '0004_alter_gameset_black_alter_gameset_white'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lobby',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lobby_code', models.TextField()),
            ],
        ),
    ]