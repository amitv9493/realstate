from drf_standardized_errors.handler import exception_handler as standardized_exception_handler
from rest_framework import status
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

    return standardized_exception_handler(exc, context)
