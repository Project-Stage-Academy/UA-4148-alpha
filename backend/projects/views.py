from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class SubscriptionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        return Response({"message": f"Subscribed to project {project_id}"}, status=status.HTTP_201_CREATED)
