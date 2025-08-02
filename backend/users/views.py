from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import UserProfile
from .serializers import UserRegistrationSerializer

from users.serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    
def send_confirmation_email(user):
    """For email sending"""
    
    print(f"[Email] Confirmation sent to: {user.email}")
    
class UserRegistrationView(generics.CreateAPIView):
    """New user registration"""
    
    queryset = UserProfile.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            send_confirmation_email(user)  # For function to send a letter

            return Response({
                "message": "Registration successful.",
                "user_id": user.id,
                "email": user.email,
                "tokens": tokens
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)