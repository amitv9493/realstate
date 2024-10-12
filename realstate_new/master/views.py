import base64
import hashlib
import hmac
import os
import time

from django.conf import settings
from django.http import Http404
from django.http import HttpResponseForbidden
from django.http import StreamingHttpResponse


def verify_token(file_path, expires_at, token):
    secret_key = settings.SECRET_KEY
    message = f"{file_path}{expires_at}".encode()
    computed_token = hmac.new(
        secret_key.encode("utf-8"),
        message,
        hashlib.sha256,
    ).digest()
    computed_token = base64.urlsafe_b64encode(computed_token).decode("utf-8")
    return computed_token == token


def file_iterator(file_name, chunk_size=8192):
    """Generator to read a file in chunks."""
    with open(file_name, "rb") as f:  # noqa: PTH123
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


def get_content_type(file_path):
    """Get the content type based on the file extension."""
    if file_path.endswith(".pdf"):
        return "application/pdf"
    if file_path.endswith((".mp4", ".m4a")):
        return "video/mp4"
    if file_path.endswith(".mp3"):
        return "audio/mpeg"
    return "application/octet-stream"  # Fallback content type


def protected_media_view(request, file_path):
    token = request.GET.get("token")
    expires_at = request.GET.get("expires")

    if not token or not expires_at:
        return HttpResponseForbidden("Access Denied: Missing token or expiry.")

    try:
        expires_at = int(expires_at)
    except ValueError:
        return HttpResponseForbidden("Access Denied: Invalid expiry time.")

    if expires_at < int(time.time()):
        return HttpResponseForbidden("Access Denied: URL has expired.")

    if not verify_token(file_path, expires_at, token):
        return HttpResponseForbidden("Access Denied: Invalid token.")

    file_full_path = os.path.join(settings.MEDIA_ROOT, file_path)  # noqa: PTH118
    if not os.path.exists(file_full_path):  # noqa: PTH110
        msg = "File not found"
        raise Http404(msg)

    content_type = get_content_type(file_path)

    response = StreamingHttpResponse(
        file_iterator(file_full_path),
        content_type=content_type,
    )
    response["Content-Length"] = os.path.getsize(file_full_path)  # noqa: PTH202
    response["Content-Disposition"] = f'inline; filename="{os.path.basename(file_full_path)}"'  # noqa: PTH119

    return response
