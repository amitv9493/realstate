import base64
import hashlib
import hmac
import os
import time
from collections import defaultdict
from urllib.parse import quote

from django.conf import settings
from django.http import Http404
from django.http import HttpResponseForbidden
from django.http import StreamingHttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from .metadata import MetaData


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
    if file_path.endswith(".jpeg"):
        return "image/jpeg"
    return "application/octet-stream"  # Fallback content type


def protected_media_view(request, file_path):
    token = request.GET.get("token")
    if "media/" in file_path:
        file_path = file_path.split("media/")[1]
    decoded_file_path = quote(file_path)
    expires_at = request.GET.get("expires")

    if not token or not expires_at:
        return HttpResponseForbidden("Access Denied: Missing token or expiry.")

    try:
        expires_at = int(expires_at)
    except ValueError:
        return HttpResponseForbidden("Access Denied: Invalid expiry time.")

    if expires_at < int(time.time()):
        return HttpResponseForbidden("Access Denied: URL has expired.")

    if not verify_token(decoded_file_path, expires_at, token):
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


class MetaDataView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        metadata = MetaData()
        data = defaultdict(list)
        ongoing_task = metadata.ongoing_task_metadata
        data["ongoingTask"] = ongoing_task
        data["createTask"].extend(
            [
                metadata.get_metadata_list(
                    type="task",
                    child="Showing",
                    fields=metadata.post_showing_metadata,
                ),
                metadata.get_metadata_list(
                    type="task",
                    child="LockBoxBS",
                    fields=metadata.post_lockbox_bs_metadata,
                ),
                metadata.get_metadata_list(
                    type="task",
                    child="LockBoxIR",
                    fields=metadata.post_lockbox_ir_metadata,
                ),
                metadata.get_metadata_list(
                    type="task",
                    child="OpenHouse",
                    fields=metadata.post_openhouse_metadata,
                ),
                metadata.get_metadata_list(
                    type="task",
                    child="Runner",
                    fields=metadata.post_runner_metadata,
                ),
                metadata.get_metadata_list(
                    type="task",
                    child="Sign",
                    fields=metadata.post_sign_metadata,
                ),
                metadata.get_metadata_list(
                    type="task",
                    child="Professional",
                    fields=metadata.post_professional_metadata,
                ),
            ],
        )
        return Response(data, 200)
