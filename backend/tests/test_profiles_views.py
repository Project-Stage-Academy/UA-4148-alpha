import pytest
from rest_framework.test import APIClient
from profiles.models import ViewedStartup

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture(autouse=True)
def clear_viewed_startups():
    ViewedStartup.objects.all().delete()


@pytest.mark.django_db
def test_startup_view_logged(api_client, create_investor, create_startup):
    investor = create_investor(email="investor1@test.com", username="investor1")
    startup = create_startup(user=investor, company_name="Startup 1")

    api_client.force_authenticate(user=investor)

    url = f"/api/profiles/startups/view/{startup.id}"
    response = api_client.post(url)

    assert response.status_code == 201
    assert "viewed successfully" in response.data["message"]


@pytest.mark.django_db
def test_list_recently_viewed_startups(api_client, create_investor, create_startup):
    investor = create_investor(email="investor2@test.com", username="investor2")
    startup = create_startup(user=investor, company_name="Startup 2")  # викликаємо функцію-фабрику

    api_client.force_authenticate(user=investor)
    api_client.post(f"/api/profiles/startups/view/{startup.id}")

    response = api_client.get("/api/profiles/startups/viewed")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["company_name"] == startup.company_name


@pytest.mark.django_db
def test_clear_viewed_startups(api_client, create_investor, create_startup):
    investor = create_investor(email="investor3@test.com", username="investor3")
    startup = create_startup(user=investor, company_name="Startup 3")

    api_client.force_authenticate(user=investor)
    api_client.post(f"/api/profiles/startups/view/{startup.id}")

    response = api_client.delete("/api/profiles/startups/viewed/clear")
    assert response.status_code == 200
    assert "cleared" in response.data["message"]

    response = api_client.get("/api/profiles/startups/viewed")
    assert len(response.data) == 0


@pytest.mark.django_db
def test_permissions_only_investors(api_client, create_startup, create_investor, startup_role):
    user = create_investor(email="startup@test.com", username="startup_user")
    user.role = startup_role
    user.save()

    startup = create_startup(user=user, company_name="Startup 1")

    api_client.force_authenticate(user=user)

    url = f"/api/profiles/startups/view/{startup.id}"
    response = api_client.post(url)

    assert response.status_code == 403
