from django.db import models
from django.contrib.auth.models import User #users

class Profile (models.Model): #profile
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    email = models.TextField()

    def __str__(self) -> str:
        return self.user.username

class GameSet (models.Model): #a collection of games, up to five
    white = models.OneToOneField(Profile, on_delete=models.SET_NULL, null=True, related_name="player_white")
    black = models.OneToOneField(Profile, on_delete=models.SET_NULL, null=True, related_name="player_black")
    white_wins = models.IntegerField(default=0)
    black_wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)

class Game (models.Model): #individual games of chess
    game_set = models.ForeignKey(GameSet, on_delete=models.SET_NULL, null=True)
    white_time = models.FloatField(180.0) #remaining chess clock time, in seconds
    black_time = models.FloatField(180.0) #as above, so below
    move_list = models.TextField()
    finished = models.BooleanField(default=False)
    winner = models.IntegerField() #0 for undecided, 1 for white, 2 for black, 3 for stalemate 

    def __str__(self) -> str:
        return f"GAME {self.id}, MOVES: {self.move_list}"
