import hashlib
from rest_framework import serializers
from users.models import PasswordResetToken, UserProfile
from users.utils import verify_reset_token
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(slug_field='role', read_only=True)
    """Serializer for user profile"""
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

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class TokenVerificationSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, data):
        raw_token = data['token']

        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        token_obj = PasswordResetToken.objects.filter(token_hash=token_hash).first()
        if not token_obj or not token_obj.is_valid():
            raise serializers.ValidationError("Invalid token.")
        
        return data

class PasswordResetSubmissionSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        raw_token = data['token']
        password = data['password']
        confirm_password = data['confirm_password']

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        token_obj = PasswordResetToken.objects.filter(token_hash=token_hash).first()
        if not token_obj or not token_obj.user:
            raise serializers.ValidationError("Invalid token.")
        
        user = token_obj.user
        try:
            validate_password(password, user)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})

       
        is_valid, message = verify_reset_token(user, raw_token)
        if not is_valid:
            raise serializers.ValidationError(message)

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
