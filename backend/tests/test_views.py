import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import UserProfile
from django.core import mail
from users.utils import generate_password_reset_token

@pytest.mark.django_db
def test_register_success():
    client = APIClient()
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "ComplexPass123!",
        "confirm_password": "ComplexPass123!",
        "first_name": "Test",
        "last_name": "User",
        "role": ''
    }
    response = client.post("/users/register/", data)
    assert response.status_code == 201
    assert UserProfile.objects.filter(email="test@example.com").exists()

@pytest.mark.django_db
def test_login_success():
    client = APIClient()
    user = UserProfile.objects.create_user(username="testuser", email="test@example.com", password="TestPass123!")
    
    response = client.post("/users/login/", {
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    assert response.status_code == 200
    assert "access" in response.data

@pytest.mark.django_db
def test_login_missing_fields():
    client = APIClient()
    response = client.post("/users/login/", {})
    assert response.status_code == 400
    assert "detail" in response.data

@pytest.mark.django_db
def test_validate_reset_token_valid():
    client = APIClient()
    user = UserProfile.objects.create_user(username="resetuser", email="reset@example.com", password="123passWord!")
    token = generate_password_reset_token(user)

    response = client.post("/users/validate-reset-token/", {
        "email": user.email,
        "token": token
    })
    assert response.status_code == 200
    assert response.data["valid"] is True

@pytest.mark.django_db
def test_validate_reset_token_invalid():
    client = APIClient()
    response = client.post("/users/validate-reset-token/", {
        "email": "noone@example.com",
        "token": "invalidtoken"
    })
    assert response.status_code == 400

@pytest.mark.django_db
def test_password_reset_sends_email(settings):
    client = APIClient()
    user = UserProfile.objects.create_user(username="emailuser", email="email@example.com", password="pass")

    response = client.post("/users/reset-password/", { "email": "email@example.com" })
    assert response.status_code == 200
    assert len(mail.outbox) == 1
    assert "reset" in mail.outbox[0].subject.lower()

@pytest.mark.django_db
def test_password_reset_submission_valid():
    client = APIClient()
    user = UserProfile.objects.create_user(username="reseter", email="reseter@example.com", password="123Pass!!")
    token = generate_password_reset_token(user)

    response = client.post("/users/reset-password-request/", {
        "email": user.email,
        "token": token,
        "password": "NewStrongPass1!",
        "confirm_password": "NewStrongPass1!"
    })

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password("NewStrongPass1!")

@pytest.mark.django_db
def test_password_reset_submission_mismatch_passwords():
    client = APIClient()
    user = UserProfile.objects.create_user(username="reseter2", email="reseter2@example.com", password="123Pass!!")
    token = generate_password_reset_token(user)

    response = client.post("/users/reset-password-request/", {
        "email": user.email,
        "token": token,
        "password": "Password1!",
        "confirm_password": "DoesNotMatch"
    })

    assert response.status_code == 400
    assert "passwords do not match" in str(response.data).lower()
