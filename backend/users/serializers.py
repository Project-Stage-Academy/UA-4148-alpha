from rest_framework import serializers
from users.models import UserProfile
from users.utils import verify_reset_token
from django.contrib.auth.password_validation import validate_password
from startups.models import StartupProfile
from investors.models import InvestorProfile


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'role']

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    # Field to distinguish between startup and investor
    representative_type = serializers.ChoiceField(
        choices=[('startup', 'Startup'), ('investor', 'Investor')],
        write_only=True
    )
    company_name = serializers.CharField(write_only=True, required=True)
    website = serializers.URLField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = UserProfile
        fields = [
            'username', 'email', 'password', 'confirm_password',
            'first_name', 'last_name', 'role',
            'representative_type', 'company_name', 'website',
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

        # Fields for type of UserProfile
        representative_type = validated_data.pop('representative_type')
        company_name = validated_data.pop('company_name')
        website = validated_data.pop('website', '')
        user = UserProfile.objects.create_user(password=password, **validated_data)
        
        # Create a profile depending on the user type
        if representative_type == 'startup':
            StartupProfile.objects.create(
            id=user.id,
            company_name=company_name,
            website=website,
            description='', #Placeholder for description and can be filled by frontend
            views_count=0
        )
        elif representative_type == 'investor':
            InvestorProfile.objects.create(
                id=user.id,
                company_name=company_name,
                website=website
            )
        
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class TokenVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()

    def validate(self, data):
        email = data['email']
        token = data['token']

        user = UserProfile.objects.filter(email=email).first()
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
        
        user = UserProfile.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("Invalid email or token.")
        
        try:
            validate_password(password, user)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})

       
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
