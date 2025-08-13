
from django.shortcuts import render, redirect
from .models import UserProfile
from rest_framework.decorators import action
from rest_framework import viewsets, status, permissions, status
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions



from .utils import generate_password_reset_token
from users.serializers import (
    PasswordResetSubmissionSerializer,
    TokenVerificationSerializer,
    PasswordResetRequestSerializer,
    UserRegistrationSerializer,
    UserSerializer
)
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

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

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
    
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"detail": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = authenticate(email=email, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "username": user.username,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role.role if user.role else None
                    }
                }, status=status.HTTP_200_OK)
    
        else: 
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


    @action(detail=False, methods=['post'], url_path='validate-reset-token')
    def validate_reset_token(self, request):
        serializer = TokenVerificationSerializer(data=request.data)
        if serializer.is_valid():
            return Response({ "valid": True, "message": "Token is valid" }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='reset-password')
    def reset_password(self, request):
        serializer = PasswordResetSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({ "message": 'Password reset successful' })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='reset-password-request')
    def reset_password_request(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        user = UserProfile.objects.filter(email=email).first()
        if user:
            token = generate_password_reset_token(user)
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            send_mail(
                subject='Reset your password',
                message=f'Click the link to reset your password: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

        return Response({"message": "If the email exist, a reset link has been send."}, status=status.HTTP_200_OK)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

