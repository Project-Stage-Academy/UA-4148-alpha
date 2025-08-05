from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

class ProjectSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()

class ProjectViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    mock_projects = [
        {"id": 1, "name": "Test Project 1", "description": "Description of Project 1"},
        {"id": 2, "name": "Test Project 2", "description": "Description of Project 2"},
    ]

    def list(self, request):
        serializer = ProjectSerializer(self.mock_projects, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        project = next((p for p in self.mock_projects if str(p["id"]) == str(pk)), None)
        if project:
            serializer = ProjectSerializer(project)
            return Response(serializer.data)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        return Response({"message": f"Subscribed to project {pk}"}, status=status.HTTP_201_CREATED)
