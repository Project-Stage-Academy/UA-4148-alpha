from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import StartupProfile, ViewedStartup
from .serializers import ViewedStartupSerializer, StartupProfileSerializer
from .permissions import IsInvestor
from django.utils import timezone
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import LimitOffsetPagination

class ViewedStartupPagination(LimitOffsetPagination):
    default_limit = 10   
    max_limit = 50

class ViewedStartupListView(generics.ListAPIView):
    serializer_class = ViewedStartupSerializer
    permission_classes = [IsInvestor]
    pagination_class = ViewedStartupPagination
    
    def get_queryset(self):
        return ViewedStartup.objects.filter(
            user=self.request.user
        ).order_by("-viewed_at")


class ViewedStartupCreateView(APIView):
    permission_classes = [IsInvestor]

    def post(self, request, startup_id):
        startup = get_object_or_404(StartupProfile, id=startup_id)

        obj, created = ViewedStartup.objects.get_or_create(
            user=request.user,
            startup=startup,
        )
        if not created:
            obj.viewed_at = timezone.now()
            obj.save()

        return Response(
            {"message": f"Startup '{startup.company_name}' viewed successfully."},
            status=status.HTTP_201_CREATED,
        )


class ClearViewedStartupsView(APIView):
    permission_classes = [IsInvestor]

    def delete(self, request):
        ViewedStartup.objects.filter(user=request.user).delete()
        return Response({"message": "Viewed startups history cleared successfully."})


class StartupViewSet(ReadOnlyModelViewSet):
    queryset = StartupProfile.objects.all()
    serializer_class = StartupProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        if request.user.is_authenticated and request.user.is_investor():
            startup = self.get_object()
            obj, created = ViewedStartup.objects.get_or_create(
                user=request.user, startup=startup
            )
            if not created:
                obj.viewed_at = timezone.now()
                obj.save()

        return response