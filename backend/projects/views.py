from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .serializers import ProjectSerializer, SubscriptionCreateSerializer
from .models import Project, Subscription, Investor
from .permissions import IsInvestor


class ProjectViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsInvestor])
    def subscribe(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)

        if project.total_funding() >= project.budget:
            return Response(
                {"error": "This project is already fully funded."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            investor = Investor.objects.get(email=request.user.email)
        except Investor.DoesNotExist:
            return Response(
                {"detail": "Only investors can subscribe."},
                status=status.HTTP_403_FORBIDDEN
            )

        data = {
            "investor": investor.id,  
            "project": pk,
            "share": request.data.get("share"),
            "investment_amount": request.data.get("investment_amount"),
        }

        serializer = SubscriptionCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(investor=investor, project=project)  
        return Response(serializer.data, status=status.HTTP_201_CREATED)
