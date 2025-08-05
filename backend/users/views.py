from django.shortcuts import render, redirect
from .models import UserProfile
from rest_framework import viewsets
from users.serializers import UserSerializer
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializers import UserRegistrationSerializer

from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    
    

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
    
    
class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

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