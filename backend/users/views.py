from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializers import UserRegistrationSerializer

class UserViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            # TODO: Implement the email sending logic

            # TODO: tokens
            return Response({
                "message": "Registration successful.",
                "user_id": user.id,
                "email": user.email,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)