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


class PropertyNotFound(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "property not found."
    default_code = "client error"

    def __init__(self, *args, property_id, **kwargs):
        self.default_detail = f"property with id {property_id} not found"
        super().__init__(*args, **kwargs)
