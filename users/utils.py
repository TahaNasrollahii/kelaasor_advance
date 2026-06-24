from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def issue_tokens_for_user(user: User) -> dict:
    """Generate JWT refresh/access tokens for the given user using Simple JWT."""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }