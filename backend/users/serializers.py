from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'role']

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = UserProfile
        fields = [
            'username', 'email', 'password', 'confirm_password',
            'first_name', 'last_name', 'role'
        ]

    def validate_password(self, value):
        """Password verification for compliance with security policies."""
        
        validate_password(value)
        return value

    def validate_email(self, value):
        """Checking the uniqueness of an email address."""
        
        if UserProfile.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("The email address is already in use.")
        return value

    def validate_username(self, value):
        """Checking the uniqueness of the username."""
        
        if UserProfile.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("The username is already taken.")
        return value

    def validate(self, data):
        """Ensure password and confirm_password match"""
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"password": "The passwords do not match."})
        return data

    def create(self, validated_data):
        """Create user with hashed password and remove confirm_password"""
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = UserProfile.objects.create_user(password=password, **validated_data)
        return user
