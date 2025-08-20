import hashlib
from datetime import timedelta

import pytest
from django.utils import timezone

from users.models import PasswordResetToken, UserProfile
from users.utils.generate_password_reset_token import generate_password_reset_token
from users.utils.verify_reset_token import verify_reset_token


@pytest.fixture
def test_user(db):
    return UserProfile.objects.create_user(
        username="testuser", email="test@example.com", password="pass123"
    )


@pytest.mark.django_db
def test_verify_reset_token_returns_true_for_valid_token(test_user):
    raw_token = generate_password_reset_token(test_user)

    is_valid, msg = verify_reset_token(test_user, raw_token)

    assert is_valid is True
    assert msg == "Token is valid"

    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    assert not PasswordResetToken.objects.filter(
        user=test_user, token_hash=token_hash
    ).exists()


@pytest.mark.django_db
def test_verify_reset_token_returns_false_for_invalid_token(test_user):
    fake_token = "invalidtokenstring"

    is_valid, msg = verify_reset_token(test_user, fake_token)

    assert is_valid is False
    assert msg == "Invalid token"


@pytest.mark.django_db
def test_verify_reset_token_returns_false_and_deletes_expired_token(test_user):
    raw_token = generate_password_reset_token(test_user)

    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    token_obj = PasswordResetToken.objects.get(user=test_user, token_hash=token_hash)
    token_obj.expires_at = timezone.now() - timedelta(minutes=1)
    token_obj.save()

    is_valid, msg = verify_reset_token(test_user, raw_token)

    assert is_valid is False
    assert msg == "Token expired"
    assert not PasswordResetToken.objects.filter(
        user=test_user, token_hash=token_hash
    ).exists()
