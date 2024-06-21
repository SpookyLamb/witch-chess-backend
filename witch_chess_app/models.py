from django.db import models
from django.contrib.auth.models import User #users

import json

class Client (models.Model): #clients and their channels
    channel_name = models.TextField()

    def __str__(self) -> str:
        return self.channel_name

class Profile (models.Model): #profile
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    email = models.TextField()

    def __str__(self) -> str:
        return self.user.username

class Lobby (models.Model): #lobbies for games
    lobby_code = models.TextField()
    white = models.OneToOneField(Client, on_delete=models.SET_NULL, null=True, related_name="player_white")
    black = models.OneToOneField(Client, on_delete=models.SET_NULL, null=True, related_name="player_black")
    private = models.BooleanField(default=False)

class GameSet (models.Model): #a collection of games, up to five
    white_wins = models.IntegerField(default=0)
    black_wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    last_state = models.TextField(default=json.dumps(None)) #stores a JSON dump of the last board state, defaults to Null (which is ignored by the front end)
    last_turn = models.TextField(default="White") #stores the next turn

class Game (models.Model): #individual games of chess
    game_set = models.ForeignKey(GameSet, on_delete=models.SET_NULL, null=True)

    start_time = models.FloatField(default=0) #time in seconds (since the epoch) when the game first started
    white_time = models.FloatField(default=180.0) #remaining chess clock time, in seconds
    black_time = models.FloatField(default=180.0) #as above, so below

    white_turns = models.IntegerField(default=0) #turns taken by white
    black_turns = models.IntegerField(default=0) #turns taken by black

    move_list = models.TextField()

    finished = models.BooleanField(default=False)
    winner = models.IntegerField(default=0) #0 for undecided, 1 for white, 2 for black, 3 for stalemate 

    def __str__(self) -> str:
        return f"GAME {self.id}, MOVES: {self.move_list}"