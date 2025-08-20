import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from .mongo_models import Room, Message

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
    if not user or not getattr(user, "is_authenticated", False):
        raise PermissionError("User must be authenticated.")
    if not other_user:
        raise ValueError("Other participant must be valid")
    if getattr(user, "role", None) != "investor":
        raise PermissionError("Only investors can initiate conversations")
    if getattr(user, "role", None) == getattr(other_user, "role", None):
        raise PermissionError("Conversation must be between investor and startup")

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
def get_message_history(room, offset=0, limit=50):
    """
    Retrieves the last N messages from the room in order.
    """
    messages = list(Message.objects(room=room).order_by("-timestamp")[offset:offset + limit])
    messages.reverse()
    return [
        {
            "id": str(msg.id),
            "sender_id": msg.sender_id,
            "first_name": msg.sender_first_name,
            "last_name": msg.sender_last_name,
            "text": msg.text,
            "timestamp": msg.timestamp.isoformat(),
            "is_read": msg.is_read,
        }
        for msg in messages
    ]


@sync_to_async
def mark_messages_as_read(room, user_id, message_ids):
    """
    Marks messages as read.
    """
    updated_ids = []
    for msg in Message.objects(id__in=message_ids, room=room, sender_id__ne=str(user_id), is_read=False):
        msg.is_read = True
        msg.save()
        updated_ids.append(str(msg.id))
    return updated_ids


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handles a new WebSocket connection.
        Validates user authentication and URL parameters,
        retrieves or creates a room, joins the user to the corresponding
        channel layer group, and accepts the WebSocket connection.
        """
        self.user = self.scope.get("user", AnonymousUser())
        other_user_id = self.scope["url_route"]["kwargs"].get("other_user_id")

        if not self.user.is_authenticated or not other_user_id:
            await self.send(text_data=json.dumps({"error": "Authentication required"}))
            await self.close()
            return

        self.other_user = await get_user(other_user_id)
        if not self.other_user:
            await self.send(text_data=json.dumps({"error": "Other user not found"}))
            await self.close()
            return

        try:
            self.room = await get_or_create_room(self.user, self.other_user)
        except PermissionError as e:
            await self.send(text_data=json.dumps({"error": str(e)}))
            await self.close()
            return

        self.room_group_name = f"chat_{self.room.name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        messages = await get_message_history(self.room)
        await self.send(text_data=json.dumps({"type": "history", "messages": messages}))

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection.
        Removes the user from the chat room group.
        """
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Handles incoming messages from the WebSocket.
        Parses and validates the message payload, saves it to MongoDB,
        and broadcasts it to all users in the room group.
        """
        if bytes_data:
            await self.send(text_data=json.dumps({"error": "Binary data not supported"}))
            await self.close()
            return

        try:
            data = json.loads(text_data or '{}')
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))
            return

        msg_type = data.get("type")

        if msg_type == "read":
            message_ids = data.get("message_ids", [])
            if not isinstance(message_ids, list):
                await self.send(text_data=json.dumps({"error": "message_ids must be a list"}))
                return
            updated = await mark_messages_as_read(self.room, self.user.id, message_ids)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "messages_read",
                    "user_id": str(self.user.id),
                    "message_ids": updated
                }
            )
            return

        if msg_type == "history":
            offset = max(int(data.get("offset", 0)), 0)
            messages = await get_message_history(self.room, offset=offset)
            await self.send(text_data=json.dumps({"type": "history", "messages": messages}))
            return

        message = (data.get('message') or '').strip()
        if not message:
            return
        if len(message) > 1000:
            await self.send(text_data=json.dumps({"error": "Message too long"}))
            return

        try:
            saved = await save_message(self.room, self.user, message)
        except Exception as e:
            await self.send(text_data=json.dumps({"error": f"Failed to save message: {str(e)}"}))
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "message": saved},
        )

    async def chat_message(self, event):
        """
        Receives a message from the room group and sends it to WebSocket clients.
        """
        await self.send(text_data=json.dumps({
            "type": "message",
            **event["message"],
        }))

    async def messages_read(self, event):
        await self.send(text_data=json.dumps({
            "type": "read",
            "user_id": event["user_id"],
            "message_ids": event["message_ids"]
        }))
