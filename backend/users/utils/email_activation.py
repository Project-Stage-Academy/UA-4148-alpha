from django.core import signing
from datetime import timedelta
from django.utils import timezone
from users.models import UserProfile
from django.conf import settings

def generate_activation_token(user):
    """
    Generate email confirmation token.
    Token is valid for 24 hours.
    """
    data_for_activation = {
        "user_id": user.id,
        "expires_at": (timezone.now() + timedelta(hours=24)).timestamp()
    }
    token = signing.dumps(data_for_activation, key=settings.SECRET_KEY)
    return token

def verify_activation_token(token):
    """
    Check email confirmation token.
    Returns user if token is valid, otherwise None + message.
    """
    try:
        data_for_activation = signing.loads(token, key=settings.SECRET_KEY)
    except signing.BadSignature:
        return None, "Invalid token"

    expires_at = timezone.datetime.fromtimestamp(data_for_activation["expires_at"], tz=timezone.utc)
    if timezone.now() > expires_at:
        return None, "The token has expired"

    user_id = data_for_activation["user_id"]
    user = UserProfile.objects.filter(id=user_id).first()
    if not user:
        return None, "User not found"

    return user, None
