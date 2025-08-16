from django.conf import settings
from django.db import models
from profiles.models import StartupProfile, InvestorProfile

class ProjectStatus(models.Model):
    status = models.CharField(max_length=150)

    def __str__(self):
        return self.status

class StartupProject(models.Model):
    subject = models.CharField(max_length=150)
    idea = models.TextField()
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    investment_needed = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.ForeignKey(ProjectStatus, on_delete=models.SET_NULL, null=True, related_name='project_statuses')
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='projects')
    investor = models.ForeignKey(InvestorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='investments')
    funding_goal = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.subject

    def total_funding(self):
        return sum(sub.share for sub in self.subscriptions.all())

    def remaining_funding(self):
        if self.funding_goal is None:
            return None
        return self.funding_goal - self.total_funding()

class SavedStartup(models.Model):
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE)
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.investor.company_name} saved {self.startup.company_name}"

class Subscription(models.Model):
    project = models.ForeignKey(StartupProject, on_delete=models.CASCADE, related_name="subscriptions")
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name="subscriptions")
    share = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.investor} -> {self.project} ({self.share})"
