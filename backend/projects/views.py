import logging
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

# Get logger for this module
logger = logging.getLogger(__name__)


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for listing, retrieving, and subscribing to projects."""

    permission_classes = [IsAuthenticated, IsInvestor]
    queryset = StartupProject.objects.all()
    serializer_class = ProjectSerializer

    def list(self, request, *args, **kwargs):
        logger.info(f"Project list request from user ID: {request.user.id}")
        try:
            queryset = self.get_queryset().order_by("-created_at")
            serializer = self.get_serializer(queryset, many=True)
            logger.debug(
                f"Successfully retrieved {len(serializer.data)} projects for user ID: {request.user.id}"
            )
            return Response(serializer.data)
        except Exception as e:
            logger.error(
                f"Error retrieving project list for user ID {request.user.id}: {str(e)}",
                exc_info=True,
            )
            return Response(
                {"detail": "Failed to retrieve projects."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, *args, **kwargs):
        logger.info(
            f"Project retrieve request from user ID: {request.user.id} for project ID: {kwargs.get('pk')}"
        )
        try:
            project = self.get_object()

            # View counter update
            StartupProject.objects.filter(pk=project.pk).update(
                views_count=F("views_count") + 1
            )
            project.refresh_from_db(fields=["views_count"])

            serializer = self.get_serializer(project)
            logger.debug(
                f"Successfully retrieved project ID: {kwargs.get('pk')} for user ID: {request.user.id}"
            )
            return Response(serializer.data)
        except Exception as e:
            logger.error(
                f"Error retrieving project ID {kwargs.get('pk')} for user ID {request.user.id}: {str(e)}",
                exc_info=True,
            )
            return Response(
                {"detail": "Failed to retrieve project."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk=None):
        logger.info(
            f"Project subscription request from user ID: {request.user.id} for project ID: {pk}"
        )
        try:
            project = StartupProject.objects.get(pk=pk)
        except StartupProject.DoesNotExist:
            logger.warning(
                f"Project subscription failed: project ID {pk} not found for user ID: {request.user.id}"
            )
            return Response(
                {"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            share = serializer.validated_data["share"]

            if project.funding_goal is None:
                logger.warning(
                    f"Project subscription failed: project ID {pk} has no funding goal for user ID: {request.user.id}"
                )
                return Response(
                    {"error": "Project has no funding goal set."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if project.remaining_funding() < share:
                logger.warning(
                    f"Project subscription failed: funding goal exceeded for project ID {pk} by user ID: {request.user.id}"
                )
                return Response(
                    {"error": "Funding goal exceeded"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subscription = serializer.save(
                investor=request.user.investorprofile, project=project
            )
            logger.info(
                f"Successfully subscribed user ID: {request.user.id} to project ID: {pk}"
            )
            return Response(
                SubscriptionSerializer(subscription).data,
                status=status.HTTP_201_CREATED,
            )

        logger.error(
            f"Project subscription failed with validation errors for user ID {request.user.id} and project ID {pk}: {serializer.errors}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def update_project(self, request, pk=None):
        logger.info(
            f"Project update request from user ID: {request.user.id} for project ID: {pk}"
        )
        try:
            project = StartupProject.objects.get(pk=pk, startup__user=request.user)
        except StartupProject.DoesNotExist:
            logger.warning(
                f"Project update failed: project ID {pk} not found or access denied for user ID: {request.user.id}"
            )
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
                logger.info(
                    f"Successfully updated project ID: {pk} with changes: {changes} by user ID: {request.user.id}"
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

        logger.error(
            f"Project update failed with validation errors for user ID {request.user.id} and project ID {pk}: {serializer.errors}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
