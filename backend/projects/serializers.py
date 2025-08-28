from rest_framework import serializers

from projects.models import StartupProject


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the StartupProject model.

    Provides a read-only representation of a startup project, including related
    fields such as the project's status, startup name, and investor name.

    """

    status = serializers.CharField(source="status.status", read_only=True)
    startup_name = serializers.CharField(source="startup.company_name", read_only=True)
    investor_name = serializers.CharField(
        source="investor.company_name", read_only=True, default=None
    )

    class Meta:
        model = StartupProject
        fields = [
            "id",
            "subject",
            "idea",
            "description",
            "website",
            "investment_needed",
            "views_count",
            "created_at",
            "updated_at",
            "status",
            "startup_name",
            "investor_name",
        ]
