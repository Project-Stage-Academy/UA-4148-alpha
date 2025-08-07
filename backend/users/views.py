from rest_framework import viewsets, status
from utils import generate_password_reset_token
from users.serializers import (
    PasswordResetSubmissionSerializer,
    TokenVerificationSerializer,
    PasswordResetRequestSerializer,
    UserRegistrationSerializer
)
from users.models import UserProfile
from rest_framework.response import Response
from rest_framework.decorators import action
from django.conf import settings
from django.core.mail import send_mail

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

    @action(detail=False, methods=['post'], url_path='validate-reset-token')
    def validate_reset_token(self, request):
        serializer = TokenVerificationSerializer(data=request.data)
        if serializer.is_valid():
            return Response({ "valid": True, "message": "Token is valid" }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='reset-password-submission')
    def verify_token(self, request):
        serializer = PasswordResetSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({ "message": 'Password reset successful' })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='password-reset')
    def password_reset(self, request):
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
