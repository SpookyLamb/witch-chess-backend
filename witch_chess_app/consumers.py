import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class MatchConsumer(WebsocketConsumer):

    def connect(self):
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
                self.lobby_group_name, {"type": "game.event", "message": self.color, "turn": None, "dispatch": "disconnect"})

        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.lobby_group_name, self.channel_name
        )

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

                if self.lobby.white != None and self.lobby.black != None: #game can start when both players are present
                    game_start = True
                    #tell any existing players the game can start
                    async_to_sync(self.channel_layer.group_send)(
                    self.lobby_group_name, {"type": "game.event", "message": game_start, "turn": None, "dispatch": "gamestart"})
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

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message, "turn": turn, "dispatch": dispatch}))
