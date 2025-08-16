import json
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .mongo_models import Room, Message
from django.utils import timezone
from django.contrib.auth import get_user_model


@sync_to_async
def get_user(user_id):
    """
    Retrieve a user by ID.
    """
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

@sync_to_async
def get_or_create_room(user, other_user):
    """
    Retrieve an existing room between two users or create a new one.
    """
    if not user or not other_user:
        raise ValueError("Both users must be valid")
    room_name = f"chat_{min(user.id, other_user.id)}_{max(user.id, other_user.id)}"
    room = Room.objects(name=room_name).first()

    if not room:
        room = Room(
            name=room_name,
            participants=[
                {
                    "id": str(user.id),
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                {
                    "id": str(other_user.id),
                    "username": other_user.username,
                    "first_name": other_user.first_name,
                    "last_name": other_user.last_name,
                },
            ],
        )
        room.save()
    return room

@sync_to_async
def save_message(room, sender, text):
    """
    Saves a message in MongoDB for the given room.
    """
    msg = Message(
        room=room,
        sender_id=str(sender.id),
        sender_first_name=sender.first_name,
        sender_last_name=sender.last_name,
        text=text,
        timestamp=timezone.now(),
        is_read=False,
    )
    msg.save()
    return {
        "id": str(msg.id),
        "sender_id": msg.sender_id,
        "first_name": msg.sender_first_name,
        "last_name": msg.sender_last_name,
        "text": msg.text,
        "timestamp": msg.timestamp.isoformat(),
        "is_read": msg.is_read,
    }

@sync_to_async
def get_message_history(room):
    """
    Retrieves the last N messages from the room in order.
    """
    messages = Message.objects(room=room).order_by("timestamp")[:50]
    return [
        {
            "sender_id": msg.sender_id,
            "sender_first_name": msg.sender_first_name,
            "sender_last_name": msg.sender_last_name,
            "text": msg.text,
            "timestamp": msg.timestamp.isoformat(),
            "is_read": msg.is_read,
        }
        for msg in messages
    ]


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handles a new WebSocket connection.
        Validates user authentication and URL parameters,
        retrieves or creates a room, joins the user to the corresponding
        channel layer group, and accepts the WebSocket connection.
        """

        # TODO: adjust when JWT with WebSocket authentication will be done
        query_params = parse_qs(self.scope["query_string"].decode())
        user_id = query_params.get("user", [None])[0]
        other_user_id = self.scope["url_route"]["kwargs"].get("other_user_id")

        # TODO: check also if user is_authenticated when JWT with WebSocket authentication will be done
        if not user_id or not other_user_id:
            await self.close()
            return

        self.user = await get_user(user_id)
        self.other_user = await get_user(other_user_id)

        if not self.other_user or not self.other_user:
            await self.close()
            return

        self.room = await get_or_create_room(self.user, self.other_user)
        self.room_group_name = f"chat_{self.room.name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        messages = await get_message_history(self.room)
        await self.send(text_data=json.dumps({
            "type": "history",
            "messages": messages
        }))

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection.
        Removes the user from the chat room group.
        """
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Handles incoming messages from the WebSocket.
        Parses and validates the message payload, saves it to MongoDB,
        and broadcasts it to all users in the room group.
        """
        try:
            data = json.loads(text_data or '{}')
        except json.JSONDecodeError:
            return

        message = (data.get('message') or '').strip()
        if not message:
            return

        saved = await save_message(self.room, self.user, message)

        await self.channel_layer.group_send(
            self.room_group_name, {
                'type': 'chat_message',
                'message': saved['text'],
                'sender_id': saved['sender_id'],
                'first_name': saved['first_name'],
                'last_name': saved['last_name'],
                'timestamp': saved['timestamp'],
                'is_read': saved['is_read'],
            },
        )

    async def chat_message(self, event):
        """
        Receives a message from the room group and sends it to WebSocket clients.
        """
        await self.send(json.dumps({
            "type": "message",
            "message": event["message"],
            "sender_id": event["sender_id"],
            "first_name": event["first_name"],
            "last_name": event["last_name"],
            "timestamp": event["timestamp"],
            "is_read": event["is_read"],
        }))
