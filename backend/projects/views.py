from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import ProjectSerializer
from .models import StartupProject
from profiles.models import InvestorProfile


class ProjectViewSet(viewsets.ViewSet):
    """ViewSet for listing, retrieving, and subscribing to projects."""

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

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk=None):
        return Response(
            {"message": f"Subscribed to project {pk}"}, status=status.HTTP_201_CREATED
        )

class ProjectViewSet(viewsets.ModelViewSet):
    """ ViewSet for listing, retrieving, and subscribing/following projects."""
    
    queryset = StartupProject.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    # action "follow" for saving projects
    @action(detail=True, methods=["post"], url_path="follow")
    def follow_projects(self, request, pk=None):
        """Allow an authenticated investor to follow (save) a startup project."""
        
        try:
            investor_profile = InvestorProfile.objects.get(user=request.user)
            project = self.get_project
            investor_profile.saved_projects.add(project)
            
            return Response(
                {"message": f"Project {project.id} has been saved to your profile."},
                status=status.HTTP_201_CREATED,
            )
        except InvestorProfile.DoesNotExist:
            return Response(
                {"error": "You must be an investor to save projects."},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
    # action "unfollow" to remove a project from saved
    @action(detail=True, method=["post"], url_path="unfollow")
    def unfollow_project(self, request, pk=None):
        """
        Allow an authenticated investor to unfollow (remove) a startup project.
        """
        
        try:
            investor_profile = InvestorProfile.objects.get(user=request.user)
            project = self.get_project()
            
            investor_profile.saved_projects.remove(project)
            
            return Response(
                {"message": f"Project {project.id} has been removed from your saved list."},
                status=status.HTTP_200_OK,
            )
        except InvestorProfile.DoesNotExist:
            return Response(
                {"error": "You must be an investor to remove saved projects."},
                status=status.HTTP_400_BAD_REQUEST,
            )