import hashlib
from rest_framework import serializers
from users.models import PasswordResetToken, UserProfile, UserRole
from users.utils import verify_reset_token
from django.contrib.auth.password_validation import validate_password
from profiles.models import StartupProfile, InvestorProfile, Industry, Location

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ["role"]

    def validate_role(self, role):
        """
        Validate that the role is within ROLE_CHOICES.
        """
        valid_roles = dict(UserRole.ROLE_CHOICES).keys()
        if role not in valid_roles:
            raise serializers.ValidationError(
                f"Available roles: {list(valid_roles)}"
            )
        if UserRole.objects.filter(role=role).exists():
            raise serializers.ValidationError(
                f"Role '{role}' already exists."
            )
        
        return role

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
        industry_id = validated_data.pop('industry_id', None)
        locations_id = validated_data.pop('locations_id', None)
        
        user = UserProfile.objects.create_user(password=password, **validated_data)
        
        profile_data = {
            'user': user,
            'company_name': company_name,
            'website': website,
        }
        
        if representative_type == 'startup':
            # Get Industry and Location objects
            def get_validation_industry_object_id(model, object_id, field_name):
                """Check if the object ID is valid and return the object."""
                
                if not object_id:
                    return None
                try:
                    return model.objects.get(id=object_id)
                except model.DoesNotExist:
                    serializers.ValidationError({field_name: f"Invalid {field_name}"})
                
            industry = get_validation_industry_object_id(Industry, industry_id, 'industry_id')
            location = get_validation_industry_object_id(Location, locations_id, 'location_id')
            
        # Create a profile depending of the user type
        if representative_type == 'startup':
            StartupProfile.objects.create(
                description='', #Placeholder for description and can be filled by frontend
                views_count=0,
                industry=industry,
                location=location,
                **profile_data
            )
        elif representative_type == 'investor':
            InvestorProfile.objects.create(**profile_data)
        
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
