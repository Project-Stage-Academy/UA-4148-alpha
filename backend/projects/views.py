from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import ProjectSerializer, SubscriptionSerializer
from .models import StartupProject as Project, Subscription
from .permissions import IsInvestor

class ProjectViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsInvestor]

    def list(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            share = serializer.validated_data["share"]

            if project.funding_goal is None:
                return Response({"error": "Project has no funding goal set."}, status=status.HTTP_400_BAD_REQUEST)

            if project.remaining_funding() < share:
                return Response({"error": "Funding goal exceeded"}, status=status.HTTP_400_BAD_REQUEST)

            subscription = serializer.save(
                investor=request.user.investorprofile, 
                project=project
            )
            return Response(SubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
