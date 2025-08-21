import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from django.urls import reverse
from projects.models import StartupProject, ProjectRevision
from profiles.models import StartupProfile
from users.models import UserProfile, UserRole

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def investor_user(db):
    role, _ = UserRole.objects.get_or_create(role="investor")
    return UserProfile.objects.create_user(
        email="investor@example.com",
        username="investor",
        password="pass123",
        role=role
    )

@pytest.fixture
def startup_project(db, investor_user):
    startup = StartupProfile.objects.create(user=investor_user, company_name="Test Startup")
    return StartupProject.objects.create(
        subject="Old Project",
        idea="Old Idea",
        startup=startup
    )

@pytest.mark.django_db
def test_update_project_creates_revision(api_client, startup_project, investor_user):
    api_client.force_authenticate(user=investor_user)
    url = reverse("project-update-project", args=[startup_project.id])

    data = {"subject": "New Project", "idea": "New Idea"}

    with patch("projects.views.get_channel_layer") as mock_layer:
        mock_channel = mock_layer.return_value
        mock_group_send = mock_channel.group_send
        response = api_client.post(url, data)

        assert response.status_code == 200
        assert response.data["project"]["subject"] == "New Project"

        revision = ProjectRevision.objects.get(project=startup_project)
        assert revision.changes["subject"]["old"] == "Old Project"
        assert revision.changes["subject"]["new"] == "New Project"

        mock_group_send.assert_called_once()
