import pytest
from users.serializers import (
    UserRegistrationSerializer,
    PasswordResetRequestSerializer,
    TokenVerificationSerializer,
    PasswordResetSubmissionSerializer
)
from users.models import UserProfile
from django.contrib.auth.password_validation import validate_password

@pytest.mark.django_db
def test_user_registration_serializer_valid_and_invalid():
    # Створюємо користувача з певною email, щоб перевірити дублікати
    UserProfile.objects.create_user(username="existinguser", email="existing@example.com", password="TestPass123!")

    # ----- Valid registration -----
    valid_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "ComplexPass123!",
        "confirm_password": "ComplexPass123!",
    }
    serializer = UserRegistrationSerializer(data=valid_data)
    assert serializer.is_valid(), serializer.errors  # valid case

    # ----- Password mismatch -----
    invalid_password_data = {
        "username": "newuser2",
        "email": "newuser2@example.com",
        "password": "ComplexPass123!",
        "confirm_password": "Mismatch123",
    }
    serializer = UserRegistrationSerializer(data=invalid_password_data)
    assert not serializer.is_valid()
    assert "password" in serializer.errors

    # ----- Duplicate email -----
    duplicate_email_data = {
        "username": "anotheruser",
        "email": "existing@example.com",  # уже існує
        "password": "ComplexPass123!",
        "confirm_password": "ComplexPass123!",
    }
    serializer = UserRegistrationSerializer(data=duplicate_email_data)
    assert not serializer.is_valid()
    assert "email" in serializer.errors

    # ----- Duplicate username -----
    UserProfile.objects.create_user(username="duplicateuser", email="dup@example.com", password="pass")

    duplicate_username_data = {
        "username": "duplicateuser",  # вже існує
        "email": "unique@example.com",
        "password": "ComplexPass123!",
        "confirm_password": "ComplexPass123!",
    }
    serializer = UserRegistrationSerializer(data=duplicate_username_data)
    assert not serializer.is_valid()
    assert "username" in serializer.errors

@pytest.mark.django_db
def test_password_reset_request_serializer():
    serializer = PasswordResetRequestSerializer(data={"email": "test@example.com"})
    assert serializer.is_valid()

@pytest.mark.django_db
def test_token_verification_serializer_valid_and_invalid():
    user = UserProfile.objects.create_user(username="testuser", email="test@example.com", password="pass123")
    # припустимо, функція verify_reset_token повертає True для тесту
    from unittest.mock import patch

    with patch("users.serializers.verify_reset_token", return_value=(True, "Token is valid")):
        data = {"email": user.email, "token": "validtoken"}
        serializer = TokenVerificationSerializer(data=data)
        assert serializer.is_valid()

    # invalid email
    data = {"email": "nope@example.com", "token": "token"}
    serializer = TokenVerificationSerializer(data=data)
    assert not serializer.is_valid()

    # invalid token (mock false)
    with patch("users.serializers.verify_reset_token", return_value=(False, "Invalid token")):
        data = {"email": user.email, "token": "badtoken"}
        serializer = TokenVerificationSerializer(data=data)
        assert not serializer.is_valid()

@pytest.mark.django_db
def test_password_reset_submission_serializer_valid_and_invalid():
    user = UserProfile.objects.create_user(username="testuser", email="test@example.com", password="pass123")
    from unittest.mock import patch

    valid_data = {
        "email": user.email,
        "token": "validtoken",
        "password": "ComplexPass123!",
        "confirm_password": "ComplexPass123!",
    }

    with patch("users.serializers.verify_reset_token", return_value=(True, "Token is valid")):
        serializer = PasswordResetSubmissionSerializer(data=valid_data)
        assert serializer.is_valid()
        serializer.save()
        user.refresh_from_db()
        assert user.check_password(valid_data["password"])

    # password mismatch
    invalid_data = valid_data.copy()
    invalid_data["confirm_password"] = "Mismatch"
    serializer = PasswordResetSubmissionSerializer(data=invalid_data)
    assert not serializer.is_valid()
    assert "Passwords do not match." in str(serializer.errors)

    # invalid email
    invalid_data = valid_data.copy()
    invalid_data["email"] = "wrong@example.com"
    with patch("users.serializers.verify_reset_token", return_value=(True, "Token is valid")):
        serializer = PasswordResetSubmissionSerializer(data=invalid_data)
        assert not serializer.is_valid()

    # invalid token
    with patch("users.serializers.verify_reset_token", return_value=(False, "Invalid token")):
        serializer = PasswordResetSubmissionSerializer(data=valid_data)
        assert not serializer.is_valid()
