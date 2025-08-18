from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from channels.exceptions import DenyConnection


User = get_user_model() #the model is taken from AUTH_USER_MODEL in settings and this is better because it is universal and not tied to a specific path

@database_sync_to_async
def get_user(user_id):
    """Asynchronously get the user by ID, or None if not found."""
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware to authenticate WebSocket connections using JWT passed in URL as ?token=<JWT>
    """
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token_list = query_params.get("token")

        scope["user"] = AnonymousUser()

        if token_list:
            token = token_list[0]
            try:
                access_token = AccessToken(token)
                user_id = access_token["user_id"]
                user = await get_user(user_id)
                if user:
                    scope["user"] = user
                else:
                    raise DenyConnection("User not found")
            except (TokenError, InvalidToken, KeyError):
                # If the token is invalid, expired or does not contain user_id, leave AnonymousUser
                raise DenyConnection("Invalid or expired token")

        return await super().__call__(scope, receive, send)