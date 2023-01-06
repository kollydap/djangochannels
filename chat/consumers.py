# chat/consumers.py
import json
from .models import Room,Message
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        self.user = self.scope["user"]
        self.room = Room.objects.get(name = self.room_name)
        self.accept()
        self.send(json.dumps({
            'type':'user_list',
            'users':[user.username for user in self.room.online.all()],
        }))
        if self.user.is_authenticated:
        # Join room group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type':'user_join',
                    'user':self.user.username,
                }
            )
            self.room.online.add(self.user)

    def user_join(self,event):
        self.send(text_data=json.dumps(event))
    def user_leave(self,event):
        self.send(text_data=json.dumps(event))

    def disconnect(self, close_code):
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,{
                    'type':'user_leave',
                    'user':self.user.username,
                }
            )
            self.room.online.remove(self.user)
        # Leave room group
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name, self.channel_name
            )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        if not self.user.is_authenticated:
            return


        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, 
            {
                "type": "chat_message", 
                "message": message,
                'user':self.user.username,
                }

        )
        Message.objects.create(user = self.user,room = self.room,content=message)
    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps(event))

# chat/consumers.py
# import json
# from .models import Room
# from channels.generic.websocket import AsyncWebsocketConsumer


# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = "chat_%s" % self.room_name
#         self.user = self.scope["user"]
#         self.room = Room.objects.get(name = self.room_name)
#         # Join room group
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)

#         await self.accept()
#         await self.channel_layer.group_send(
#             self.room_group_name, {"type": "chat_message", "message": "Someone New Joined"}
#         )

       

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]
#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name, {"type": "chat_message", "message": message}
#         )

#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event["message"]
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({"message": message,"sender":str(self.user)}))