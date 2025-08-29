from django.db import models
from django.conf import settings
from profiles.models import InvestorProfile, StartupProfile


class StartupProject(models.Model):
    """Represents a project created by a startup, including investment details."""

    subject = models.CharField(max_length=150)
    idea = models.TextField()
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    investment_needed = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        FUNDED = "FUNDED", "Funded"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    startup = models.ForeignKey(
        StartupProfile, on_delete=models.CASCADE, related_name="projects"
    )

    def __str__(self):
        return self.subject


class SavedProject(models.Model):
    """Intermediate table for represents a project saved by investor (many-to-many relation)."""

    investor = models.ForeignKey(
        InvestorProfile,
        on_delete=models.CASCADE,
        related_name="investor_saved_projects",
    )

    project = models.ForeignKey(
        StartupProject, on_delete=models.CASCADE, related_name="saved_by_investors"
    )

    saved_at = models.DateTimeField(
        auto_now_add=True, help_text="Date and time the project was saved"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["investor", "project"], name="uniq_investor_project"
            )  # protection against duplicates: one investor cannot save one startup twice
        ]
        ordering = ["-saved_at"]
        verbose_name = "Saved project"
        verbose_name_plural = "Saved projects"

    def __str__(self):
        return f"{self.investor.company_name} saved project {self.project.subject} from {self.project.startup.company_name}"


class ProjectRevision(models.Model):
    project = models.ForeignKey(
        StartupProject, on_delete=models.CASCADE, related_name="revisions"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    changes = models.JSONField()
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Revision of {self.project.subject} at {self.updated_at}"
