from rest_framework import status
from rest_framework.renderers import JSONRenderer


class Custom200Renderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context["response"]

        if status.is_success(response.status_code):
            response.status_code = status.HTTP_200_OK

        return super().render(data, accepted_media_type, renderer_context)
