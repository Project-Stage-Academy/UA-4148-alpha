from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .mongo_models import Room, Message

User = get_user_model()

class ParticipantSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)


class RoomSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    participants = ParticipantSerializer(many=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    name = serializers.CharField(read_only=True)

    def validate_participants(self, value):
        """
        Validate that:
        - Exactly 2 participants exist
        - Both exist in DB
        - Current user is included
        - One is investor, one is startup
        """
        participant_ids = []
        for p in value:
            try:
                participant_ids.append(int(p["id"]))
            except (KeyError, ValueError, TypeError):
                raise serializers.ValidationError("Invalid participant ID")

        if len(participant_ids) != 2:
            raise serializers.ValidationError("Room must have exactly 2 participants")

        existing_users = list(User.objects.filter(id__in=participant_ids))
        if len(existing_users) != 2:
            raise serializers.ValidationError("One or more participants do not exist")

        request_user = self.context["request"].user
        if request_user.id not in participant_ids:
            raise serializers.ValidationError("You must be a participant in the room")

        roles = {u.role for u in existing_users}
        if roles != {"investor", "startup"}:
            raise serializers.ValidationError("Room must be between an investor and a startup")

        return value

    def create(self, validated_data):
        participants_data = validated_data["participants"]
        participant_ids = sorted(int(p["id"]) for p in participants_data)

        room_name = f"chat_{participant_ids[0]}_{participant_ids[1]}"

        room = Room.objects(name=room_name).first()
        if not room:
            room = Room(
                name=room_name,
                participants=participants_data,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
            room.save()
        return room


class MessageSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    room_id = serializers.CharField(write_only=True)
    sender_id = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    text = serializers.CharField()
    timestamp = serializers.DateTimeField(read_only=True)
    is_read = serializers.BooleanField(read_only=True)

    def validate(self, attrs):
        room_id = attrs.get("room_id")
        user = self.context["request"].user

        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise serializers.ValidationError({"room_id": "Room not found."})

        if not any(str(p["id"]) == str(user.id) for p in room.participants):
            raise serializers.ValidationError("You are not a participant of this room.")

        text = attrs.get("text", "").strip()
        if not text:
            raise serializers.ValidationError({"text": "Message cannot be empty"})
        if len(text) > 1000:
            raise serializers.ValidationError({"text": "Message too long (max 1000 chars)"})

        text = attrs.get("text", "").strip()
        if not text:
            raise serializers.ValidationError({"text": "Message cannot be empty"})
        if len(text) > 1000:
            raise serializers.ValidationError({"text": "Message too long (max 1000 chars)"})

        attrs["room"] = room
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        room = validated_data["room"]

        message = Message(
            room=room,
            sender_id=str(user.id),
            sender_first_name=user.first_name,
            sender_last_name=user.last_name,
            text=validated_data["text"],
            timestamp=timezone.now(),
            is_read=False,
        )
        message.save()
        return message
