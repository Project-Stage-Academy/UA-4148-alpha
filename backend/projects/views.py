from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import StartupProjectSerializer
from .models import StartupProject, ProjectRevision
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class ProjectViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  

    mock_projects = [
        {"id": 1, "name": "Test Project 1", "description": "Description of Project 1"},
        {"id": 2, "name": "Test Project 2", "description": "Description of Project 2"},
    ]

    def list(self, request):
        serializer = StartupProjectSerializer(self.mock_projects, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        project = next((p for p in self.mock_projects if str(p["id"]) == str(pk)), None)
        if project:
            serializer = StartupProjectSerializer(project)
            return Response(serializer.data)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        return Response(
            {"message": f"Subscribed to project {pk}"},
            status=status.HTTP_201_CREATED
        )
        
        
    @action(detail=True, methods=['post'])
    def update_project(self, request, pk=None):
        try:
            project = StartupProject.objects.get(pk=pk, startup__user=request.user)
        except StartupProject.DoesNotExist:
            return Response(
                {"detail": "Project not found or access denied."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StartupProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            old_data = StartupProjectSerializer(project).data
            serializer.save()
            new_data = serializer.data

            changes = {
                field: {"old": old_data[field], "new": new_data[field]}
                for field in new_data
                if old_data[field] != new_data[field]
            }

            if changes:
                ProjectRevision.objects.create(
                    project=project,
                    updated_by=request.user,
                    changes=changes
                )

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"startup_{project.startup.id}",
                {
                    "type": "project.update",
                    "project": new_data
                }
            )

            return Response(
                {"message": "Project updated successfully", "project": new_data},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)