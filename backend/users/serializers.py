from rest_framework import serializers
from django.contrib.auth import get_user_model
from backend.users.utils import verify_reset_token

User = get_user_model()

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']
        
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class TokenVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()

    def validate(self, data):
        email = data['email']
        token = data['token']

        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("Invalid email or token.")
        
        is_valid, message = verify_reset_token(user, token)
        if not is_valid:
            raise serializers.ValidationError(message)
        
        data['user'] = user
        return data

class PasswordResetSubmissionSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        email = data['email']
        token = data['token']
        password = data['password']
        confirm_password = data['confirm_password']

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("Invalid email or token.")
        
        is_valid, message = verify_reset_token(user, token)
        if not is_valid:
            raise serializers.ValidationError(message)

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        password = self.validated_data['password']
        user.set_password(password)
        user.save()