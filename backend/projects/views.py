from rest_framework import status, viewsets, generics, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import F
from django.db import transaction

from django_filters.rest_framework import DjangoFilterBackend

from profiles.models import InvestorProfile
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .serializers import ProjectSerializer, SubscriptionSerializer
from .models import StartupProject, Subscription, ProjectRevision
from .permissions import IsInvestor, IsStartup


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for listing, retrieving, and subscribing to projects."""

    permission_classes = [IsAuthenticated, IsInvestor]
    queryset = StartupProject.objects.all()
    serializer_class = ProjectSerializer

    # Filters for base List
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["subject", "idea", "description", "startup__company_name"]
    ordering_fields = ["created_at", "views_count", "funding_goal"]

    def get_permissions(self):
        if self.action in ["create"]:
            permission_classes = [IsAuthenticated, IsStartup]
        elif self.action in ["list", "retrieve", "save", "unsave"]:
            permission_classes = [IsAuthenticated, IsInvestor]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Creation a project is automatically link it to a startup"""
        startup_profile = getattr(self.request.user, "startupprofile", None)
        if not startup_profile:
            raise Exception("Startup profile not found for this user.")
        serializer.save(startup=startup_profile)

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
        project.refresh_from_db(fields=["views_count"])
        serializer = self.get_serializer(project)

        return Response(serializer.data)

    # Follow for saving projects by investor
    @action(detail=True, methods=["post"], url_path="save")
    def save(self, request, pk=None):
        """
        POST  /api/startups/{pk}/save/
        Allow an authenticated investor to follow (save) a startup project.
        """

        investor_profile = getattr(request.user, "investorprofile", None)
        if not investor_profile:
            return Response(
                {"error": "Investor profile not found for this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )
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
            {
                "message": f"Project {project.id} has been saved to your profile.",
                "project": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    # Unfollow / delete to remove a project from saved
    @action(detail=True, methods=["post", "delete"], url_path="unsave")
    def unsave(self, request, pk=None):
        """
        Allow an authenticated investor to unfollow (remove) a startup project.
        supports POST /api/projects/{pk}/unsave/ and DELETE /api/projects/{pk}/unsave/
        """

        investor_profile = getattr(request.user, "investorprofile", None)
        if not investor_profile:
            return Response(
                {"error": "Investor profile not found for this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project = self.get_object()

        # Atomic transaction to ensure database integrity
        with transaction.atomic():
            investor_profile.saved_projects.remove(project)

        serializer = ProjectSerializer(project)

        if request.method == "DELETE":
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {
                "message": f"Project {project.id} has been removed from your saved list.",
                "project": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk=None):
        try:
            project = self.get_object()
        except StartupProject.DoesNotExist:
            return Response(
                {"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            share = serializer.validated_data["share"]

            if project.funding_goal is None:
                return Response(
                    {"error": "Project has no funding goal set."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if project.remaining_funding() < share:
                return Response(
                    {"error": "Funding goal exceeded"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subscription = serializer.save(
                investor=request.user.investorprofile, project=project
            )
            return Response(
                SubscriptionSerializer(subscription).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def update_project(self, request, pk=None):
        try:
            project = StartupProject.objects.get(pk=pk, startup__user=request.user)
        except StartupProject.DoesNotExist:
            return Response(
                {"detail": "Project not found or access denied."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            old_data = ProjectSerializer(project).data
            serializer.save()
            new_data = serializer.data

            changes = {
                field: {"old": old_data[field], "new": new_data[field]}
                for field in new_data
                if old_data[field] != new_data[field]
            }

            if changes:
                ProjectRevision.objects.create(
                    project=project, updated_by=request.user, changes=changes
                )

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"startup_{project.startup.id}",
                {"type": "project.update", "project": new_data},
            )

            return Response(
                {"message": "Project updated successfully", "project": new_data},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SavedProjectsList(generics.ListAPIView):
    """
    GET /api/investor/saved-projects/
    Forms a list of projects that the current investor has saved.
    - search: GET /api/investor/saved-projects/?search=AI;
    - ordering: GET /api/investor/saved-projects/?ordering=funding_goal.

    Requires authentication and investor role.
    Response: JSON list of saved projects.
    """

    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsInvestor]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["subject", "idea", "description", "startup__company_name"]
    ordering_fields = ["created_at", "views_count", "funding_goal"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        investor_profile = getattr(user, "investorprofile", None)

        if not investor_profile:
            raise PermissionDenied("Investor profile not found for this user.")

        if not getattr(investor_profile, "is_active", True):
            raise PermissionDenied("Account of user is not active.")

        return investor_profile.saved_projects.all()
