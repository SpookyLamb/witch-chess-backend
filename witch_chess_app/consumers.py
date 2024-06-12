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

        self.accept()

        # To reject the connection, call:
        # we should reject the connection if there are already two players (two channels in the group)
        #self.close()
    
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.lobby_group_name, self.channel_name
        )

    # Receive message from WebSocket, which we then forward to game_event, which then sends it (individually) back to everyone in the group
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.lobby_group_name, {"type": "game.event", "message": message}
            # Event has a 'type' key corresponding to the name of the method invoked on consumers that receive the event
            # This translation is done by replacing . with _, thus, game.event calls the game_event method
        )

    # Receive message from lobby group, then forward that to individual players
    def game_event(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))

    # def receive(self, text_data):
    #     #receives a message and echoes it back to the same client that sent it

    #     text_data_json = json.loads(text_data)
    #     message = text_data_json["message"]

    #     self.send(text_data=json.dumps({"message": message}))

# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         # Make a database row with our channel name
#         Clients.objects.create(channel_name=self.channel_name)
#     def disconnect(self, close_code):
#         # Note that in some rare cases (power loss, etc) disconnect may fail
#         # to run; this naive example would leave zombie channel names around.
#         Clients.objects.filter(channel_name=self.channel_name).delete()
#     def chat_message(self, event):
#         # Handles the "chat.message" event when it's sent to us.
#         self.send(text_data=event["text"])