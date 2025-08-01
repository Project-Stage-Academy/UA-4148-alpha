from django.db import models

class UserRole(models.Model):
    role = models.CharField(max_length=50)

    def __str__(self):
        return self.role

class UserModel(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.CharField(unique=True)
    password_hash = models.CharField(max_length=128)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE)

    def __str__(self):
        return self.username