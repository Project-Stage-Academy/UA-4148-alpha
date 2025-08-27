from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import F

from .serializers import ProjectSerializer
from .models import StartupProject
from profiles.models import InvestorProfile


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
            views_count=F("views_count") + 1
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