from rest_framework import serializers
from .mongo_models import Room, Message


class ParticipantSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)


class RoomSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    participants = ParticipantSerializer(many=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class MessageSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    room = serializers.CharField()
    sender_id = serializers.CharField()
    sender_first_name = serializers.CharField()
    sender_last_name = serializers.CharField()
    text = serializers.CharField()
    timestamp = serializers.DateTimeField()
    is_read = serializers.BooleanField()
