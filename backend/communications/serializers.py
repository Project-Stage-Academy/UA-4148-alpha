from rest_framework import serializers
from .mongo_models import Room, Message


class ParticipantSerializer(serializers.Serializer):
    id = serializers.CharField()
    username = serializers.CharField()
    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)


class RoomSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    participants = ParticipantSerializer(many=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    name = serializers.CharField(read_only=True)

class MessageSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    room_id = serializers.CharField(source="room.id")
    sender_id = serializers.CharField()
    first_name = serializers.CharField(source="sender_first_name")
    last_name = serializers.CharField(source="sender_last_name")
    text = serializers.CharField()
    timestamp = serializers.DateTimeField()
    is_read = serializers.BooleanField()
