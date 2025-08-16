from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class InvestorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.company_name or self.user.username


class StartupProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=150)

    def __str__(self):
        return self.company_name
