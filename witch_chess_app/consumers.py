import json
import time
from threading import Timer
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class MatchConsumer(WebsocketConsumer):

    def connect(self):
        #init
        self.turn = None
        self.time_remaining = 180.0
        self.game_set = None

        self.lobby_code = self.scope["url_route"]["kwargs"]["lobby_code"]
        self.lobby_group_name = f"lobby_{self.lobby_code}"

        async_to_sync(self.channel_layer.group_add)(
            self.lobby_group_name, self.channel_name
        )

        from witch_chess_app.models import Client #these imports have to be done within the class - doing them at the top crashes Django
        from witch_chess_app.models import Lobby

        # Make a database row with our channel name
        client = Client.objects.create(channel_name=self.channel_name)
        client.save()

        # check if there is an existing game with the given lobby_code
        lobby = Lobby.objects.filter(lobby_code=self.lobby_code)

        if not lobby: #Queryset is empty
            #create a new lobby and add yourself as "white"
            lobby = Lobby.objects.create(lobby_code=self.lobby_code, white=client)
            lobby.save()
            self.color = "White" #set color, passed to client later

        else: #Queryset has results
            #an existing lobby is more complex, we need to check which color is "None"
            #check white, then black, if both AREN'T None (there are players present), join as a spectator
            lobby = lobby[0]
            
            if lobby.white == None: #white
                lobby.white = client
                lobby.save()
                self.color = "White"
            elif lobby.black == None: #black
                lobby.black = client
                lobby.save()
                self.color = "Black"
            else: #spectator
                self.color = "Spectate"
        
        self.lobby = lobby #save lobby for later

        # finally, accept the connection
        self.accept()
    
    def disconnect(self, close_code):
        # send a message to anyone remaining in the lobby that this client has disconnected
        async_to_sync(self.channel_layer.group_send)(
                self.lobby_group_name, {"type": "player.disconnect", "message": self.color, "dispatch": "disconnect"})

        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.lobby_group_name, self.channel_name
        )

        self.turn = None #kill any running timers

        # Note that in some rare cases (power loss, etc) disconnect may fail
        # to run; this naive example would leave zombie channel names around.
        from witch_chess_app.models import Client
        Client.objects.filter(channel_name=self.channel_name).delete()

    # Receive message from WebSocket, which we then forward to game_event, which then sends it (individually) back to everyone in the group
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        turn = text_data_json["turn"]
        dispatch = text_data_json["dispatch"]

        match dispatch:
            case "init":
                game_start = False

                #send initialization information back to the client
                self.send(text_data=json.dumps({"dispatch": "initial", "color": self.color}))

                #also takes the client's privacy request, only accepts it if the client is WHITE, since P1 is the lobby creator
                #message is a boolean, saves as the lobby's "private" marker
                
                if self.color == "White":
                    self.lobby.private = message
                    self.lobby.save()

                if self.lobby.white != None and self.lobby.black != None: #game can start when both players are present
                    game_start = True
                    #tell any existing players the game can start, ignore spectators
                    if self.color != "Spectate":
                        async_to_sync(self.channel_layer.group_send)(
                        self.lobby_group_name, {"type": "begin.game", "message": game_start, "dispatch": "gamestart"})

            case "echo-gamestart":
                #sent when a GAME SET STARTS, aka the first round
                #the BLACK client should create the gameset here, and then silently send its id to the rest of the group

                if self.color == "Black":
                    from witch_chess_app.models import GameSet #likewise as the imports in connect()

                    new_set = GameSet.objects.create() #defaults are all fine

                    async_to_sync(self.channel_layer.group_send)(
                    self.lobby_group_name, {"type": "save.set", "set": new_set.id})

                self.turn = "White" #begin tracking the current turn
                self.timer() #initiate timer
            
            case "echo-nextround":
                #sent when a NEW ROUND starts, never the first round

                print(self.color, "nextround")

                self.reset() #reset game vars
                self.timer() #re-init timer

            case "game-over":
                #does end of game logic here, "message" is the winner, "turn" is blank
                #counts wins and usually, though not always, starts a new round
                #only a count a win if self.color matches the winner, and only count a draw if self.color is Black, to prevent multi-counting
                #the set ends when:
                    #the next round would be round 6 (or more, somehow)
                    #one player already has 3 (or more, somehow) wins
                #otherwise start a new round
                self.turn = None

                from witch_chess_app.models import GameSet
                game_set = GameSet.objects.get(pk=self.game_set)

                if self.color == message: #count our wins, add to the GameSet
                    if self.color == "White":
                        game_set.white_wins += 1
                        game_set.save()
                    else:
                        game_set.black_wins += 1
                        game_set.save()
                elif message == "Draw" and self.color == "Black":
                    game_set.draws += 1
                    game_set.save()
                
                if self.color == "Black": #only Black handles starting new rounds (also starts the game by default, due to being P2)
                    if game_set.white_wins + game_set.black_wins + game_set.draws < 5:
                        #wait 1.1 seconds to allow any leftover timers to stop, then start a new round
                        round_timer = Timer(1.1, self.new_game)
                        round_timer.start()

            case "gamestate":
                #send message containing the current game state to the lobby group
                async_to_sync(self.channel_layer.group_send)(
                self.lobby_group_name, {"type": "game.event", "message": message, "turn": turn, "dispatch": "gamestate"}
                # Event has a 'type' key corresponding to the name of the method invoked on consumers that receive the event
                # This translation is done by replacing . with _, thus, game.event calls the game_event method
            )
            
            case _:
                print("Bad data received by client!")

    # Receive message from lobby group, then forward that to individual players
    def game_event(self, event):
        message = event["message"]
        turn = event["turn"]
        dispatch = event["dispatch"]

        self.turn = turn #update current turn

        if self.color != "Spectate":
            if self.turn != self.color: #"my" player's turn just ended
                self.time_remaining += 2 #when a player's turn ends, they get a little time back
                async_to_sync(self.channel_layer.group_send)( #forward to the group
                self.lobby_group_name, {"type": "time.event", "color": self.color, "time": self.time_remaining})
            
            self.timer() #initiate timers

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message, "turn": turn, "dispatch": dispatch}))
    
    # recieved when a player disconnects
    def player_disconnect(self, event):
        message = event["message"]
        dispatch = event["dispatch"]
        self.send(text_data=json.dumps({"message": message, "dispatch": dispatch}))

    # recieved when a game begins
    def begin_game(self, event):
        message = event["message"]
        dispatch = event["dispatch"]
        self.send(text_data=json.dumps({"message": message, "dispatch": dispatch}))

    # recieves a message regarding a player's remaining time, and forwards that to the group
    def time_event(self, event):
        color = event["color"]
        new_time = event["time"]

        self.send(text_data=json.dumps({"new_time": new_time, "color": color, "dispatch": "time"}))
    
    def time_out(self, event):
        color = event["color"]

        self.send(text_data=json.dumps({"color": color, "dispatch": "timeout"}))

        self.reset()

    def decrement_time(self):

        if self.color == self.turn:
            self.time_remaining -= 1

            if self.time_remaining <= 0:
                #tell the room that a player has timed out
                async_to_sync(self.channel_layer.group_send)(
                self.lobby_group_name, {"type": "time.out", "color": self.color})
                return

            #forward to the group
            async_to_sync(self.channel_layer.group_send)(
            self.lobby_group_name, {"type": "time.event", "color": self.color, "time": self.time_remaining})
            
            return self.timer()
        else:
            return
    
    def save_set(self, event):
        #save the newly created set's ID to our game_set var, don't do anything else
        self.game_set = event["set"] 

    def timer(self):
        #decrements the internal timer for a player

        if self.color == self.turn:
            timer = Timer(1.0, self.decrement_time)
            timer.start()
            return
        else:
            return
    
    def reset(self):
        #reset game vars back to their starting state
        self.turn = "White"
        self.time_remaining = 180.0

    def new_game(self):
        async_to_sync(self.channel_layer.group_send)(
        self.lobby_group_name, {"type": "begin.game", "message": True, "dispatch": "next-round"})
