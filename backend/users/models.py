from django.db import models
from django.contrib.auth.models import AbstractUser

class UserRole(models.Model):
    role = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.role

class UserProfile(AbstractUser):
    """Custom user model extending Django's AbstractUser"""
    email = models.EmailField(unique=True)
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return self.email
