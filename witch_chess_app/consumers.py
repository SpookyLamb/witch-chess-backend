import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class MatchConsumer(WebsocketConsumer):
    #groups = ["broadcast"]

    def connect(self):
        self.accept()

        # To reject the connection, call:
        #self.close()

    def receive(self, text_data):
        #receives a message and echoes it back to the same client that sent it

        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))

    def disconnect(self, close_code):
        # Called when the socket closes
        pass

# class TextRoomConsumer(WebsocketConsumer):

#     def connect(self):

#         self.room_name = self.scope\['url_route'\]['kwargs']['room_name']
#         self.room_group_name = 'chat_%s' % self.room_name
#         # Join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )
#         self.accept()

#     def disconnect(self, close_code):
#         # Leave room group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name,
#             self.channel_name
#         )

#     def receive(self, text_data):
#         # Receive message from WebSocket
#         text_data_json = json.loads(text_data)
#         text = text_data_json['text']
#         sender = text_data_json['sender']
#         # Send message to room group
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': text,
#                 'sender': sender
#             }
#         )

#     def chat_message(self, event):
#         # Receive message from room group
#         text = event['message']
#         sender = event['sender']
#         # Send message to WebSocket
#         self.send(text_data=json.dumps({
#             'text': text,
#             'sender': sender
#         }))

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