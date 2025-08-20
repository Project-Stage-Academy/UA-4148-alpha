import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handles a new WebSocket connection.
        Joins the user to the chat room group based on 'room_name' from the URL.
        """
        # Authorization check for connections only for authorized users
        user = self.scope.get("user", AnonymousUser())
        if not user or not user.is_authenticated:
            await self.send(text_data=json.dumps({"error": "Authentication required"}))
            await self.close()
            return

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection.
        Removes the user from the chat room group.
        """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Receive a message from the WebSocket client.
        Validates JSON format and presence of 'message' key,
        then sends it to the room group.
        """
        try:
            data = json.loads(text_data or "{}")
            message = data.get("message")
            if not message:
                return
        except json.JSONDecodeError:
            return

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    async def chat_message(self, event):
        """
        Receives a message from the room group abd sends it to WebSocket clients.
        """
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
