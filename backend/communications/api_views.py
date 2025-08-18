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
    Safe membership check with string coercion.
    """
    uid = str(user_id)
    return any(str(p.get("id")) == uid for p in (room.participants or []))


def _validate_participants_exist(participants_ids):
    """
    Return (ok, missing_ids) indicating which participant IDs are missing from the Django DB.
    """
    User = get_user_model()
    existing_ids = set(User.objects.filter(id__in=participants_ids).values_list("id", flat=True))
    missing = [pid for pid in participants_ids if pid not in existing_ids]
    return len(missing) == 0, missing


class RoomViewSet(viewsets.ViewSet):
    """
    Conversations (Rooms)
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        List all rooms the user participates in.
        """
        rooms = Room.objects(participants__id=str(request.user.id))
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new room (conversation).
        """
        participants = request.data.get("participants", [])
        if not isinstance(participants, list) or not participants:
            return Response({"error": "participants must be a non-empty list"}, status=400)

        try:
            participant_ids = [int(p["id"]) for p in participants if "id" in p]
        except (TypeError, ValueError):
            return Response({"error": "participants[].id must be integers"}, status=400)

        if request.user.id not in participant_ids:
            return Response({"error": "you must be a participant of the room you create"}, status=400)

        ok, missing = _validate_participants_exist(participant_ids)
        if not ok:
            return Response({"error": f"users not found: {missing}"}, status=400)

        room_name = "_".join(sorted(str(uid) for uid in participant_ids))
        User = get_user_model()
        users = User.objects.filter(id__in=participant_ids)

        room = Room.objects(name=room_name).first()
        if not room:
            normalized = [
                {
                    "id": str(u.id),
                    "username": u.username,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                }
                for u in users
            ]
            room = Room(name=room_name, participants=normalized)
            room.save()
        else:
            already = {str(p["id"]) for p in room.participants or []}
            for u in users:
                if str(u.id) not in already:
                    room.participants.append({
                        "id": str(u.id),
                        "username": u.username,
                        "first_name": u.first_name,
                        "last_name": u.last_name,
                    })
            room.save()

        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="messages")
    def messages(self, request, pk=None):
        """
        Retrieve last 50 messages from a room (chronological).
        """
        try:
            room = Room.objects.get(id=pk)
        except Room.DoesNotExist:
            return Response({"error": "room not found"}, status=404)

        if not _user_in_room(room, request.user.id):
            return Response({"error": "not a participant of this room"}, status=403)

        messages = list(Message.objects(room=room).order_by("-timestamp")[:50])
        messages.reverse()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="read")
    def mark_as_read(self, request, pk=None):
        """
        Marks all messages in the room as read for the current user.
        """
        try:
            room = Room.objects.get(id=pk)
        except Room.DoesNotExist:
            return Response({"error": "room not found."}, status=404)

        if not _user_in_room(room, request.user.id):
            return Response({"error": "not a participant of this room"}, status=403)

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
            status=200,
        )


class MessageViewSet(viewsets.ViewSet):
    """
    Messages (send)
    """
    permission_classes = [IsAuthenticated]

    def create(self, request):
        """
        Send a new message in a room.
        """
        room_id = request.data.get("room")
        text = (request.data.get("text") or "").strip()

        if not room_id or not text:
            return Response({"error": "room and text required"}, status=400)

        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "room not found"}, status=404)

        if not _user_in_room(room, request.user.id):
            return Response({"error": "not a participant of this room"}, status=403)

        sender = request.user
        message = Message(
            room=room,
            sender_id=str(sender.id),
            sender_first_name=sender.first_name,
            sender_last_name=sender.last_name,
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
