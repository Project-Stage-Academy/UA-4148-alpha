import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from users.models import UserProfile
from profiles.models import InvestorProfile, StartupProfile
from projects.models import StartupProject


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def investor_user(db):
    user = UserProfile.objects.create_user(
        username="investor", password="testpass", role="investor"
    )
    InvestorProfile.objects.create(user=user)
    return user


@pytest.fixture
def startup_user(db):
    user = UserProfile.objects.create_user(
        username="startup", password="testpass", role="startup"
    )
    StartupProfile.objects.create(user=user, company_name="Test Company")
    return user


@pytest.fixture
def project(startup_user):
    startup_profile = startup_user.startupprofile
    return StartupProject.objects.create(
        startup=startup_profile,
        subject="AI Project",
        idea="AI for healthcare",
        description="Test project",
        funding_goal=10000,
    )


@pytest.mark.django_db
def test_investor_can_list_saved_startups(api_client, investor_user, project):
    investor_profile = investor_user.investorprofile
    investor_profile.saved_projects.add(project)

    api_client.force_authenticate(user=investor_user)
    url = reverse(
        "saved-startups",
        kwargs={"user_id": investor_user.id, "investor_id": investor_profile.id},
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == project.id


@pytest.mark.django_db
def test_non_investor_cannot_list_saved_startups(api_client, startup_user):
    api_client.force_authenticate(user=startup_user)
    url = reverse(
        "saved-startups", kwargs={"user_id": startup_user.id, "investor_id": 999}
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_investor_can_unsave_startup(api_client, investor_user, project):
    investor_profile = investor_user.investorprofile
    investor_profile.saved_projects.add(project)

    api_client.force_authenticate(user=investor_user)
    url = reverse(
        "project-unsave", kwargs={"startup_id": project.id}
    )  # adapt name if different
    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert not investor_profile.saved_projects.filter(pk=project.id).exists()


@pytest.mark.django_db
def test_startup_cannot_unsave_startup(api_client, startup_user, project):
    api_client.force_authenticate(user=startup_user)
    url = reverse("project-unsave", kwargs={"startup_id": project.id})
    response = api_client.post(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
