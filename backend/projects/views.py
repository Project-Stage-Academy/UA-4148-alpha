from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import F
from django.db import transaction

from profiles.models import InvestorProfile
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import ProjectSerializer, SubscriptionSerializer
from .models import StartupProject, Subscription, ProjectRevision
from .permissions import IsStartup
from django.shortcuts import get_object_or_404


class ProjectViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    """ViewSet for listing, retrieving, and subscribing to projects."""

    permission_classes = [IsAuthenticated]
    queryset = StartupProject.objects.all()
    serializer_class = ProjectSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["subject"]
    search_fields = ["subject"]

    def get_permissions(self):
        if self.action in ["create"]:
            permission_classes = [IsAuthenticated, IsStartup]
        elif self.action in ["list", "retrieve", "save", "unsave"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        startup_profile = getattr(self.request.user, "startupprofile", None)
        if not startup_profile:
            startup_id = self.request.data.get("startup")
            if startup_id:
                from .models import StartupProfile

                startup_profile = StartupProfile.objects.get(pk=startup_id)
            else:
                raise Exception("Startup profile not found for this user.")
        serializer.save(owner=self.request.user, startup=startup_profile)

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

    # Unfollow" to remove a project from saved
    @action(detail=True, methods=["post"], url_path="unsave")
    def unsave(self, request, pk=None):
        """Allow an authenticated investor to unfollow (remove) a startup project."""

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

        return Response(
            {
                "message": f"Project {project.id} has been removed from your saved list.",
                "project": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk=None):
        project = get_object_or_404(StartupProject, pk=pk)

        try:
            from profiles.models import InvestorProfile

            investor = InvestorProfile.objects.get(user=request.user)
        except InvestorProfile.DoesNotExist:
            return Response(
                {"error": "User is not an investor."}, status=status.HTTP_403_FORBIDDEN
            )

        if Subscription.objects.filter(project=project, investor=investor).exists():
            return Response(
                {"error": "Already subscribed"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SubscriptionSerializer(
            data=request.data, context={"project": project}
        )
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

            subscription = serializer.save(investor=investor, project=project)
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
