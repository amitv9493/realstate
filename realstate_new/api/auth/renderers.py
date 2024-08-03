import json

from rest_framework import renderers


class UserRenderes(renderers.JSONRenderer):
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return json.dumps({"errors": data}) if "ErrorDetail" in str(data) else json.dumps(data)
