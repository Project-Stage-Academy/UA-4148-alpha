from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserRole(models.Model):
    role = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.role
    
class UserProfileManager(BaseUserManager):
    """Managing class for the UserProfile model"""
    
    def create_user(self, email, password, **extra_fields):
        """Creating a new user with low-level email validation as a protection against direct incorrect calling and validation of the django primary field before user authentication"""
        
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Creating a superuser with additional administrator rights"""
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    
class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Модель профілю користувача"""
    
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email
    