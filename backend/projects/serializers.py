from rest_framework import serializers
from .models import StartupProject

class StartupProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = StartupProject
        fields = [
            'id',
            'subject',
            'idea',
            'description',
            'website',
            'investment_needed',
            'status',
            'startup',
            'investor',
            'views_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['startup', 'investor', 'views_count', 'created_at', 'updated_at']

    def validate_subject(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Subject must be at least 3 characters long.")
        return value

    def validate_idea(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Idea cannot be empty.")
        return value
