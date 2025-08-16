from django.core import signing
from django.utils import timezone
from users.models import UserProfile

def generate_activation_token(user):
    """
    Generate email confirmation token.
    Token is valid for 24 hours.
    """
    data_for_activation = {"user_id": user.id}
    signer = signing.TimestampSigner()
    token = signer.sign_object(data_for_activation)
    return token

def verify_activation_token(token, max_age = 86400): # max_age = 24 hours in seconds
    """
    Check email confirmation token.
    Returns user if token is valid, otherwise None + message.
    """
    
    signer = signing.TimestampSigner()
    
    try:
        data_for_activation = signer.unsign_object(token, max_age = max_age)
    except signing.SignatureExpired:
        return None, "The token has expired"
    except signing.BadSignature:
        return None, "Invalid token"

    user_id = data_for_activation["user_id"]
    user = UserProfile.objects.filter(id=user_id).first()
    if not user:
        return None, "User not found"

    return user, None
