
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from projects.models import StartupProject, Subscription
from profiles.models import StartupProfile, InvestorProfile

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def startup_role(db):
    from users.models import UserRole
    return UserRole.objects.get_or_create(role="startup")[0]

@pytest.fixture
def investor_role(db):
    from users.models import UserRole
    return UserRole.objects.get_or_create(role="investor")[0]

@pytest.fixture
def user(db, startup_role):
    return User.objects.create_user(username="user1", email="user1@example.com", password="pass1234", role=startup_role)


@pytest.fixture
def user2(db, investor_role):
    return User.objects.create_user(username="user2", email="user2@example.com", password="pass1234", role=investor_role)


@pytest.fixture
def startup_profile(db, user):
    return StartupProfile.objects.create(user=user, company_name="Test Startup")


@pytest.fixture
def investor_profile(db, user2):
    profile =  InvestorProfile.objects.create(user=user2, company_name="Investor Inc.")
    return profile

@pytest.fixture
def project(db, user, startup_profile):
    return StartupProject.objects.create(
        subject="Test Project",
        idea="Some idea",
        description="Description",
        owner=user,
        startup=startup_profile,
        investment_needed=True,
        funding_goal=100000.00,
    )


@pytest.mark.django_db
def test_create_project(api_client, user, startup_profile):
    api_client.force_authenticate(user=user)
    url = reverse("project-list")
    data = {
        "subject": "New Project",
        "idea": "New idea",
        "description": "Some description",
        "startup": startup_profile.id,
        "investment_needed": True,
        "funding_goal": "50000.00",
    }
    response = api_client.post(url, data)
    print("RESPONSE DATA:", response.data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["subject"] == "New Project"
    assert response.data["owner"] == user.id


@pytest.mark.django_db
def test_list_projects(api_client, user, project):
    api_client.force_authenticate(user=user)
    url = reverse("project-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert any(p["id"] == project.id for p in response.data)


@pytest.mark.django_db
def test_update_project(api_client, user, project):
    api_client.force_authenticate(user=user)
    url = reverse("project-update-project", args=[project.id])
    data = {"subject": "Updated Project"}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["project"]["subject"] == "Updated Project"


@pytest.mark.django_db
def test_delete_project(api_client, user, project):
    api_client.force_authenticate(user=user)
    url = reverse("project-detail", args=[project.id])
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not StartupProject.objects.filter(id=project.id).exists()


@pytest.mark.django_db
def test_subscribe_project(api_client, user2, investor_profile, project):
    api_client.force_authenticate(user=user2)
    url = reverse("project-subscribe", args=[project.id])
    data = {"share": 20000.00}
    response = api_client.post(url, data)
    print("RESPONSE DATA:", response.data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Subscription.objects.filter(project=project, investor=investor_profile).exists()

@pytest.mark.django_db
def test_duplicate_subscription(api_client, user2, investor_profile, project):
    api_client.force_authenticate(user=user2)
    url = reverse("project-subscribe", args=[project.id])
    data = {"share": "20000.00"}
    api_client.post(url, data)
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
