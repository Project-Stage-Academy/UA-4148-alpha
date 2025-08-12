from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="password_reset_token"
        verbose_name = "Password reset token"
        verbose_name_plural = "Password reset tokens"
        indexes = [
            models.Index(fields=["token_hash"]),
        ]

    def is_valid(self):
        return timezone.now() < self.expires_at

    def __str__(self):
        return f"Token for {self.user.email} (expires {self.expires_at})"

class Role(models.TextChoices):
    INVESTOR = "INVESTOR", "Investor"
    STARTUP = "STARTUP", "Startup"

class UserRole(models.Model):
    role = models.CharField(max_length=50, unique=True, choices=Role.choices)

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
