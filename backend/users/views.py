from rest_framework.decorators import action
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import UserRegistrationSerializer, UserSerializer

class UserViewSet(viewsets.ViewSet):
    """
    A ViewSet for handling user-related operations:
    - Registration
    - Viewing own profile
    - Password reset (placeholder)
    """

    def get_permissions(self):
        """
        Set permissions dynamically based on action.
        Public access allowed for registration and password reset.
        """
        if self.action in ['register', 'reset_password']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """
        Register a new user.
        """
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

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Return the authenticated user's profile data.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='reset-password')
    def reset_password(self, request):
        """
        Placeholder for password reset functionality.
        """
        return Response({"message": "Password reset not implemented yet."}, status=status.HTTP_501_NOT_IMPLEMENTED)
