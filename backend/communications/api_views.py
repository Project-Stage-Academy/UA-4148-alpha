from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .mongo_models import Room, Message
from .serializers import RoomSerializer, MessageSerializer

def _user_in_room(room: Room, user_id):
    """
    Check membership safely, ids stored as strings in Mongo.
    """
    return any(str(p.get("id")) == str(user_id) for p in room.participants or [])


class RoomViewSet(viewsets.ViewSet):
    """
    Conversations (Rooms)
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        List all rooms the user participates in (newest first).
        """
        rooms = Room.objects(participants__id=str(request.user.id)).order_by("-updated_at")
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="messages")
    def messages(self, request, pk=None):
        """
        Retrieve last 50 messages from a room (chronological).
        """
        try:
            room = Room.objects.get(id=pk)
        except Room.DoesNotExist:
            return Response({"error": "room not found"}, status=status.HTTP_404_NOT_FOUND)

        if not _user_in_room(room, request.user.id):
            return Response({"error": "not a participant of this room"}, status=status.HTTP_403_FORBIDDEN)

        messages = list(Message.objects(room=room).order_by("-timestamp")[:50])
        messages.reverse()
        return Response(MessageSerializer(messages, many=True).data)

    @action(detail=True, methods=["post"], url_path="read")
    def mark_as_read(self, request, pk=None):
        """
        Marks all messages in the room as read for the current user.
        """
        try:
            room = Room.objects.get(id=pk)
        except Room.DoesNotExist:
            return Response({"error": "room not found."}, status=status.HTTP_404_NOT_FOUND)

        if not _user_in_room(room, request.user.id):
            return Response({"error": "not a participant of this room"}, status=status.HTTP_403_FORBIDDEN)

        unread = Message.objects(room=room, is_read=False, sender_id__ne=str(request.user.id))
        ids = [str(m.id) for m in unread]
        unread.update(set__is_read=True)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{room.name}",
            {"type": "messages_read", "user_id": str(request.user.id), "message_ids": ids},
        )

        return Response(
            {
                "detail": f"{len(ids)} messages marked as read.",
                "message_ids": ids,
                "user_id": str(request.user.id)
            },
            status=status.HTTP_200_OK,
        )


class MessageViewSet(viewsets.ViewSet):
    """
    Messages (send)
    """
    permission_classes = [IsAuthenticated]

    def create(self, request):
        """
        Send a new message. Auto-creates room if it doesn't exist — but only investors can start.
        """
        other_user_id = request.data.get("other_user_id")
        text = (request.data.get("text") or "").strip()

        if not other_user_id or not text:
            return Response({"error": "other_user_id and text are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            other_user_id = int(other_user_id)
        except (ValueError, TypeError):
            return Response({"error": "other_user_id must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        if other_user_id == request.user.id:
            return Response({"error": "cannot message yourself"}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return Response({"error": "Recipient user not found"}, status=status.HTTP_404_NOT_FOUND)

        sender_role = getattr(getattr(request.user, "role", None), "role", None)
        receiver_role = getattr(getattr(other_user, "role", None), "role", None)

        if sender_role not in {"investor", "startup"} or receiver_role not in {"investor", "startup"}:
            return Response({"error": "messaging allowed only between investor and startup"},
                            status=status.HTTP_400_BAD_REQUEST)

        if sender_role == receiver_role:
            return Response({"error": "messaging allowed only between investor and startup"},
                            status=status.HTTP_400_BAD_REQUEST)

        a, b = sorted([str(request.user.id), str(other_user_id)])
        room_name = f"chat_{a}_{b}"
        room = Room.objects(name=room_name).first()

        if not room and sender_role != "investor":
            return Response({"error": "only investors can start a new conversation"}, status=status.HTTP_403_FORBIDDEN)

        if not room:
            participants = [
                {
                    "id": str(request.user.id),
                    "username": request.user.username,
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                },
                {
                    "id": str(other_user.id),
                    "username": other_user.username,
                    "first_name": other_user.first_name,
                    "last_name": other_user.last_name,
                },
            ]
            room = Room(name=room_name, participants=participants)
            room.save()

        message = Message(
            room=room,
            sender_id=str(request.user.id),
            sender_first_name=request.user.first_name,
            sender_last_name=request.user.last_name,
            text=text,
        )
        message.save()

        serializer = MessageSerializer(message).data

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{room.name}",
            {"type": "chat_message", "message": serializer},
        )

        return Response(serializer, status=status.HTTP_201_CREATED)
