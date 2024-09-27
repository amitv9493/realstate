from djangorestframework_camel_case.settings import api_settings
from djangorestframework_camel_case.util import camelize
from rest_framework import status


class CamelCaseJSONRenderer(api_settings.RENDERER_CLASS):
    json_underscoreize = api_settings.JSON_UNDERSCOREIZE

    def render(
        self,
        data,
        accepted_media_type=None,
        renderer_context=None,
        *args,
        **kwargs,
    ):
        response = renderer_context.get("response") if renderer_context else None

        if status.is_success(response.status_code):
            response.status_code = status.HTTP_200_OK

        return super().render(
            camelize(data, **self.json_underscoreize),
            *args,
            **kwargs,
        )
