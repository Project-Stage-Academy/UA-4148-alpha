from django.db import models
from django.conf import settings
# Create your models here.

class Industry(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class StartupProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='startups')
    company_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    views_count = models.IntegerField(default=0)
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, blank=True, related_name='startups')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='startup_locations')

    def __str__(self):
        return self.company_name

class InvestorProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='investors')
    company_name = models.CharField(max_length=150)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.company_name
