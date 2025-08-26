from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import (
    PasswordResetRequestSerializer,
    PasswordResetSubmissionSerializer,
    TokenVerificationSerializer,
    UserRegistrationSerializer,
    UserRoleSerializer,
    UserSerializer,
)
from users.utils.email_activation import (
    generate_activation_token,
    verify_activation_token,
)
from users.utils.email_utils import send_activation_email

from .models import UserProfile, UserRole
from .permissions import InvestorRolePermission, StartupRolePermission
from .utils import generate_password_reset_token


class UserViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing user-related operations including:
    - User registration and activation
    - Login
    - Switching roles
    - Viewing own profile
    - Password reset requests and submissions
    - Token validation
    """

    def get_permissions(self):
        """
        Set permissions dynamically based on action.
        Public access allowed for registration and password reset.
        """
        if self.action == "me":
            return [IsAuthenticated()]
        if self.action == "by-role":
            return [IsAuthenticated(), InvestorRolePermission()]
        if self.action in [
            "create_role",
            "login",
            "register",
            "reset_password",
            "validate_reset_token",
            "reset_password_request",
        ]:
            return [AllowAny()]
        return [IsAuthenticated()]

    # TODO: remove /me route after testing
    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = UserSerializer(user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="by-role")
    def by_role(self, request):
        """
        Returns users filtered by role.
        """
        role = request.query_params.get("role")
        if not role:
            return Response(
                {"detail": "Role is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        if role not in ("investor", "startup"):
            return Response(
                {"detail": "Invalid role value."}, status=status.HTTP_400_BAD_REQUEST
            )
        users = UserProfile.objects.filter(role__role=role)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # TODO: only admins can create roles. remove create_role from get_permissions once implemented
    @action(detail=False, methods=["post"], url_path="create-role")
    def create_role(self, request):
        """
        Create the user's role.
        """
        serializer = UserRoleSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            role = serializer.validated_data["role"]
            new_role = UserRole.objects.create(role=role)
            return Response(
                {"message": f"Role {new_role.role} created."},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="switch-role")
    def switch_role(self, request):
        """
        Switch the user's role.
        """
        user = request.user
        role_id = request.data.get("role_id")
        if not role_id:
            return Response(
                {"detail": "Role ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        role = UserRole.objects.filter(id=role_id).first()
        if not role:
            return Response(
                {"detail": "Role does not exist."}, status=status.HTTP_404_NOT_FOUND
            )

        user.role = role
        user.save()
        return Response(
            {"message": "Role switched successfully."}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        """
        Register a new user.
        """
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Login blocking until activation
            user.is_active = False
            user.save(update_fields=["is_active"])

            # Generate a token and send a letter
            token = generate_activation_token(user)
            send_activation_email(token, user.email)

            # TODO: tokens
            return Response(
                {
                    "message": "Registration successful.",
                    "user_id": user.id,
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="activate")
    def activate(self, request):
        """
        Confirm email by token.
        Expects POST with JSON body: {"token": "<activation_token>"}
        """
        token = request.data.get("token")
        if not token:
            return Response(
                {"detail": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        user, error = verify_activation_token(token)
        if not user:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])

        return Response(
            {"detail": "Account activated successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"], url_path="resend-activation")
    def resend_activation(self, request):
        """
        Resend activation email to a user who has not activated their account.
        Expects POST with JSON body: {"email": "<user_email>"}
        """
        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = UserProfile.objects.filter(email=email).first()
        if not user:
            # From a security perspective, the message does not reveal the existence of the email.
            return Response(
                {"detail": "If the email exists, an activation link has been sent."},
                status=status.HTTP_200_OK,
            )

        if user.is_active:
            return Response(
                {"detail": "Account is already active."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate a new activation token and send the email
        token = generate_activation_token(user)
        send_activation_email(token, user.email)

        return Response(
            {"detail": "If the email exists, an activation link has been sent."},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"detail": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = authenticate(email=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "username": user.username,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.role.role if user.role else None,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    @action(detail=False, methods=["post"], url_path="validate-reset-token")
    def validate_reset_token(self, request):
        serializer = TokenVerificationSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"valid": True, "message": "Token is valid"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="reset-password")
    def reset_password(self, request):
        serializer = PasswordResetSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset successful"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="reset-password-request")
    def reset_password_request(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        user = UserProfile.objects.filter(email=email).first()
        if user:
            token = generate_password_reset_token(user)
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            send_mail(
                subject="Reset your password",
                message=f"Click the link to reset your password: {reset_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

        return Response(
            {"message": "If the email exist, a reset link has been send."},
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    API endpoint for logging out users by blacklisting their refresh tokens.
    Requires authentication via JWT.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT
            )
        except (KeyError, TokenError, InvalidToken) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
