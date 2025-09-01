import logging
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import ProjectSerializer

# Get logger for this module
logger = logging.getLogger(__name__)


class ProjectViewSet(viewsets.ViewSet):
    """ViewSet for listing, retrieving, and subscribing to projects."""

    permission_classes = [IsAuthenticated]

    mock_projects = [
        {"id": 1, "name": "Test Project 1", "description": "Description of Project 1"},
        {"id": 2, "name": "Test Project 2", "description": "Description of Project 2"},
    ]

    def list(self, request):
        logger.info(f"Project list request from user ID: {request.user.id}")
        try:
            serializer = ProjectSerializer(self.mock_projects, many=True)
            logger.debug(f"Successfully retrieved {len(self.mock_projects)} projects for user ID: {request.user.id}")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving project list for user ID {request.user.id}: {str(e)}", exc_info=True)
            return Response(
                {"detail": "Failed to retrieve projects."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, pk=None):
        logger.info(f"Project retrieve request from user ID: {request.user.id} for project ID: {pk}")
        try:
            project = next((p for p in self.mock_projects if str(p["id"]) == str(pk)), None)
            if project:
                serializer = ProjectSerializer(project)
                logger.debug(f"Successfully retrieved project ID: {pk} for user ID: {request.user.id}")
                return Response(serializer.data)
            logger.warning(f"Project ID: {pk} not found for user ID: {request.user.id}")
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving project ID {pk} for user ID {request.user.id}: {str(e)}", exc_info=True)
            return Response(
                {"detail": "Failed to retrieve project."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk=None):
        logger.info(f"Project subscription request from user ID: {request.user.id} for project ID: {pk}")
        try:
            # Check if project exists
            project = next((p for p in self.mock_projects if str(p["id"]) == str(pk)), None)
            if not project:
                logger.warning(f"Project subscription failed: project ID {pk} not found for user ID: {request.user.id}")
                return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
            
            logger.info(f"Successfully subscribed user ID: {request.user.id} to project ID: {pk}")
            return Response(
                {"message": f"Subscribed to project {pk}"}, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error subscribing user ID {request.user.id} to project ID {pk}: {str(e)}", exc_info=True)
            return Response(
                {"detail": "Failed to subscribe to project."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
