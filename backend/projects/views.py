from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.response import Response
from django.db.models import F
from django.db import transaction

from .serializers import ProjectSerializer
from .models import StartupProject
from profiles.models import InvestorProfile


class IsStartup(BasePermission):
    """Allow only startups to create projects"""
    def has_permission(self, request, view):
        return str(getattr(request.user, "role", "")) == 2 #Returns True or False to allow access
    
class IsInvestor(BasePermission):
    """Allow only investors to view/follow projects"""
    def has_permission(self, request, view):
        return str(getattr(request.user, "role", "")) == 1 #Returns True or False to allow access
    
class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for listing, retrieving, and subscribing to projects."""
    queryset = StartupProject.objects.all()
    serializer_class = ProjectSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [IsAuthenticated, IsStartup]
        elif self.action in ['list', 'retrieve', 'save_project', 'unsave_project']:
            permission_classes = [IsAuthenticated, IsInvestor]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Creation a project is automatically link it to a startup"""
        serializer.save(startup=self.request.user.startupprofile)

    def list(self, request, *args, **kwargs):
        """Viewing projects by investors"""
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
    
    # Follow for saving projects by investor
    @action(detail=True, methods=["post"], url_path="follow")
    def save_project(self, request, pk=None):
        """Allow an authenticated investor to follow (save) a startup project."""
        
        investor_profile = request.user.investorprofile
        project = self.get_object()
        
        # Prevent duplicates
        if investor_profile.saved_projects.filter(pk=project.pk).exists():
            serializer = ProjectSerializer(project)
            return Response(
                {"message": "Project is already saved.", "project": serializer.data},
                status=status.HTTP_200_OK,
            )
        
        # Atomic transaction to ensure database integrity
        with transaction.atomic():
            investor_profile.saved_projects.add(project)
        
        serializer = ProjectSerializer(project)
        
        return Response(
            {"message": f"Project {project.id} has been saved to your profile.",
             "project": serializer.data},
            status=status.HTTP_201_CREATED,
        )
            
    # Unfollow" to remove a project from saved
    @action(detail=True, methods=["post"], url_path="unfollow")
    def unsave_project(self, request, pk=None):
        """Allow an authenticated investor to unfollow (remove) a startup project."""
        investor_profile = request.user.investorprofile
        project = self.get_object()
        
        # Atomic transaction to ensure database integrity
        with transaction.atomic():
            investor_profile.saved_projects.remove(project)
        
        serializer = ProjectSerializer(project)
        
        return Response(
            {"message": f"Project {project.id} has been removed from your saved list.",
             "project": serializer.data},
            status=status.HTTP_200_OK,
        )
        