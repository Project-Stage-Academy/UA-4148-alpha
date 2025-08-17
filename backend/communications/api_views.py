from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .mongo_models import Room, Message
from .serializers import RoomSerializer, MessageSerializer


class RoomViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """List all rooms the user participates in"""
        user_id = request.user.id
        rooms = Room.objects(participants__id=user_id)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create new conversation"""
        participants = request.data.get("participants", [])
        if not participants:
            return Response({"error": "Participants required"}, status=400)

        room_name = "-".join(sorted(str(uid) for uid in participants))

        room, created = Room.objects.get_or_create(name=room_name)
        for p in participants:
            if not any(str(p["id"]) == str(u["id"]) for u in room.participants):
                room.participants.append(p)
        room.save()

        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        """Send a new message in a room (auto-create if needed)"""
        room_id = request.data.get("room")
        text = request.data.get("text")

        if not room_id or not text:
            return Response({"error": "room and text required"}, status=400)

        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=404)

        sender = request.user
        message = Message(
            room=room,
            sender_id=str(sender.id),
            sender_first_name=sender.first_name,
            sender_last_name=sender.last_name,
            text=text,
        ).save()

        serializer = MessageSerializer(message)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{room.id}",
            {
                "type": "chat_message",
                "message": serializer.data,
            },
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        """Retrieve last 50 messages from a room"""
        try:
            room = Room.objects.get(id=pk)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=404)

        messages = Message.objects(room=room).order_by("-timestamp")[:50]
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
