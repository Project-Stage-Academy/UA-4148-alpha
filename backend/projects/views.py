from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import F
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .serializers import ProjectSerializer, SubscriptionSerializer
from .models import StartupProject, Subscription, ProjectRevision
from .permissions import IsInvestor


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for listing, retrieving, and subscribing to projects."""

    permission_classes = [IsAuthenticated, IsInvestor]
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
        project.refresh_from_db(fields=["views_count"])

        serializer = self.get_serializer(project)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk=None):
        try:
            project = StartupProject.objects.get(pk=pk)
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
                    {"error": "Funding goal exceeded"}, status=status.HTTP_400_BAD_REQUEST
                )

            subscription = serializer.save(
                investor=request.user.investorprofile,
                project=project
            )
            return Response(
                SubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED
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
