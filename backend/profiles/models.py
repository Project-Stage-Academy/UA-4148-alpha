from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Startup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='startups')
    company_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    views_count = models.IntegerField(default=0)
    field_of_activity = models.IntegerField(default=0)
    location = models.IntegerField(default=0)
    startup_logo = models.ImageField(upload_to='logos/startup_logos/', blank=True)

    def __str__(self):
        return self.company_name

class Investor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investors')
    company_name = models.CharField(max_length=150)
    website = models.URLField(blank=True)
    field_of_activity = models.IntegerField(default=0)
    location_id = models.IntegerField(default=0)
    investor_logo = models.ImageField(upload_to='logos/investor_logos/', blank=True)

    def __str__(self):
        return self.company_name
