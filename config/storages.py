import base64
import hashlib
import hmac
import time
from urllib.parse import urlencode

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class ExpiringURLFileStorage(FileSystemStorage):
    def generate_token(self, file_path, expires_at):
        secret_key = settings.SECRET_KEY  # Use Django's secret key for token generation

        # Create a token by signing both file path and expiry time
        message = f"{file_path}{expires_at}".encode()
        token = hmac.new(secret_key.encode("utf-8"), message, hashlib.sha256).digest()

        # Base64 encode the token for use in URLs
        return base64.urlsafe_b64encode(token).decode("utf-8")

    def url(self, name, expiry_time=3600):
        file_url = super().url(name)
        token_url = file_url.split("media/")[1]
        expires_at = int(time.time()) + expiry_time

        # Generate the access token and expiry timestamp
        token = self.generate_token(token_url, expires_at)

        # Append the token and expiry timestamp to the URL as query parameters
        return f'{file_url}?{urlencode({"token": token, "expires": expires_at})}'
