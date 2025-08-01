from django.db import models
from profiles.models import Startup, Investor

# Create your models here.
class ProjectStatus(models.Model):
    status = models.CharField(max_length=150)

    def __str__(self):
        return self.status

class StartupProject(models.Model):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='projects')
    subject = models.CharField(max_length=150)
    idea = models.TextField()
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)

    investment_needed = models.IntegerField(default=0)
    views = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.ForeignKey(ProjectStatus, on_delete=models.SET_NULL, related_name='status')

    def __str__(self):
        return self.subject

class ProjectFile(models.Model):
    project = models.ForeignKey(StartupProject, on_delete=models.CASCADE, related_name='files')
    file_url = models.FileField(upload_to='project_files/')
    file_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_type} for {self.project.subject}"