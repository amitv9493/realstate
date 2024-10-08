from rest_framework import status
from rest_framework.exceptions import APIException


class MissingFieldError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Required fields missing."
    default_code = "field_missing_error"


class PaymentVerificationFailedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Unable to verify payment."
    default_code = "payment_verification_failed"
