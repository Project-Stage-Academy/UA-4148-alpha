from rest_framework.decorators import action
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import UserRegistrationSerializer, UserSerializer

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

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='reset-password', permission_classes=[permissions.AllowAny])
    def reset_password(self, request):
        return Response({"message": "Password reset not implemented yet."}, status=status.HTTP_501_NOT_IMPLEMENTED)

