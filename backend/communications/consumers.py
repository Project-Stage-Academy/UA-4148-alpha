import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .mongo_models import Room, Message
from django.utils import timezone


@sync_to_async
def get_or_create_room(room_name, user_data):
    """
    Finds an existing room or create a new one.
    Adds the connecting user to participants if not already in the room.
    """
    room = Room.objects(name=room_name).first()
    if not room:
        room = Room(name=room_name)
        room.save()

    room.add_participant(
        user_id=user_data.get('id'),
        username=user_data.get('username'),
        first_name=user_data.get('first_name'),
        last_name=user_data.get('last_name'),
    )
    return room

@sync_to_async
def save_message(room, sender_data, text):
    """
    Saves a message in MongoDB for the given room.
    """
    msg = Message(
        room=room,
        sender_id=str(sender_data.get('id')),
        sender_first_name=sender_data.get('first_name'),
        sender_last_name=sender_data.get('last_name'),
        text=text,
        timestamp=timezone.now(),
    )
    msg.save()
    return {
        'text': msg.text,
        'sender_id': msg.sender_id,
        'sender_first_name': msg.sender_first_name,
        'sender_last_name': msg.sender_last_name,
        'timestamp': msg.timezone.isoformat(),
    }


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handles a new WebSocket connection.
        Joins the user to the chat room group based on 'room_name' from the URL.
        """
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        user = self.scope.get('user')
        self.user_data = {
            'id': getattr(user, 'id', None) or 'anon',
            'username': getattr(user, 'username', 'Anonymous'),
            'first_name': getattr(user, 'first_name', ''),
            'last_name': getattr(user, 'last_name', ''),
        }

        if not self.room_name:
            await self.close()
            return

        self.room_group_name = f'chat_{self.room_name}'
        self.room = await get_or_create_room(self.room_name, self.user_data)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(json.dumps({
            'type': 'system',
            'message': f'{self.user_data['username']} joined the room.'
        }))

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection.
        Removes the user from the chat room group.
        """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Receive a message from the WebSocket, saves it and broadcasts it.
        Validates JSON format and presence of 'message' key,
        then sends it to the room group.
        """
        try:
            data = json.loads(text_data or '{}')
        except json.JSONDecodeError:
            return

        message = data.get('message' or '').strip()
        if not message:
            return

        saved = await save_message(self.room, self.user_data, text)

        await self.channel_layer.group_send(
            self.room_group_name, {
                'type': 'chat_message',
                'message': saved['message'],
                'sender_id': saved['sender_id'],
                'sender_first_name': saved['sender_first_name'],
                'sender_last_name': saved['sender_last_name'],
                'timestamp': saved['timestamp'],
            }
        )

    async def chat_message(self, event):
        """
        Receives a message from the room group and sends it to WebSocket clients.
        """
        await self.send(json.dumps({
            "type": "message",
            "message": event["message"],
            "sender_id": event["sender_id"],
            "sender_first_name": event["sender_first_name"],
            "sender_last_name": event["sender_last_name"],
            "timestamp": event["timestamp"],
        }))
