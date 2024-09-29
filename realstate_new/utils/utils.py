from datetime import timedelta

from django.core import signing
from django.utils.timezone import now


def generate_reset_token(user):
    data = {
        "user_id": user.id,
        "email": user.email,
        "timestamp": str(now() + timedelta(minutes=10)),  # 10-minute expiration
    }
    # Sign the token with Django's signing utility
    return signing.dumps(data, salt="password-reset-salt")
