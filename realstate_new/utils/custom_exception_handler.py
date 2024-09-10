from drf_standardized_errors.handler import exception_handler as standardized_exception_handler
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.exceptions import TokenError


def custom_exception_handler(exc, context):
    if isinstance(exc, (InvalidToken, TokenError)):
        return Response(
            {
                "type": "client_error",
                "errors": [
                    {
                        "code": "token_not_valid",
                        "detail": "Token is invalid or expired",
                        "attr": "detail",
                    },
                ],
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    response = standardized_exception_handler(exc, context)

    if response is not None:
        if (
            isinstance(exc, APIException) and 400 <= response.status_code < 500  # noqa: PLR2004
        ):
            response.status_code = status.HTTP_200_OK

        else:
            response.status_code = status.HTTP_200_OK

    return response
