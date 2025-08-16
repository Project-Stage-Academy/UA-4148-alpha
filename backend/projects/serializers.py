from rest_framework import serializers
from .models import StartupProject, Subscription


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = StartupProject
        fields = ["id", "subject", "idea", "description", "website", "investment_needed", "views_count", "created_at"]


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "project", "share"]

    def validate(self, data):
        project = data["project"]
        share = data["share"]

        if not hasattr(project, "funding_goal") or project.funding_goal is None:
            raise serializers.ValidationError("This project has no funding goal set.")

        if project.remaining_funding() < share:
            raise serializers.ValidationError("Funding goal already reached or share too high.")

        return data
