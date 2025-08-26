from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import F

from .serializers import ProjectSerializer
from .models import StartupProject


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for listing, retrieving, and subscribing to projects."""

    permission_classes = [IsAuthenticated]
    queryset = StartupProject.objects.all()
    serializer_class = ProjectSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().order_by("-created_at")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        project = self.get_object()
        
        # View counter update
        StartupProject.objects.filter(pk=project.pk).update(
            views_count = F("views_count")+1
        )
        
        # Updating the object (project) to give the serializer the current value
        project.refresh_from_db(fields=["views_count"])
        
        serializer = self.get_serializer(project)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk=None):
        return Response(
            {"message": f"Subscribed to project {pk}"}, status=status.HTTP_201_CREATED
        )
