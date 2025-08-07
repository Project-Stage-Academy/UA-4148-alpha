import pytest
import hashlib
from django.utils import timezone
from datetime import timedelta
from users.models import PasswordResetToken, UserProfile
from users.utils.verify_reset_token import verify_reset_token
from users.utils.generate_password_reset_token import generate_password_reset_token

@pytest.mark.django_db
def test_verify_reset_token_returns_true_for_valid_token():
    user = UserProfile.objects.create_user(username="testuser", email="test@example.com", password="pass123")
    raw_token = generate_password_reset_token(user)
    
    is_valid, msg = verify_reset_token(user, raw_token)
    
    assert is_valid is True
    assert msg == "Token is valid"
    
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    assert not PasswordResetToken.objects.filter(user=user, token_hash=token_hash).exists()


@pytest.mark.django_db
def test_verify_reset_token_returns_false_for_invalid_token():
    user = UserProfile.objects.create_user(username="testuser", email="test@example.com", password="pass123")
    fake_token = "invalidtokenstring"
    
    is_valid, msg = verify_reset_token(user, fake_token)
    
    assert is_valid is False
    assert msg == "Invalid token"


@pytest.mark.django_db
def test_verify_reset_token_returns_false_and_deletes_expired_token():
    user = UserProfile.objects.create_user(username="testuser", email="test@example.com", password="pass123")
    raw_token = generate_password_reset_token(user)
    
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    token_obj = PasswordResetToken.objects.get(user=user, token_hash=token_hash)
    token_obj.expires_at = timezone.now() - timedelta(minutes=1)
    token_obj.save()
    
    is_valid, msg = verify_reset_token(user, raw_token)
    
    assert is_valid is False
    assert msg == "Token expired"
    assert not PasswordResetToken.objects.filter(user=user, token_hash=token_hash).exists()
