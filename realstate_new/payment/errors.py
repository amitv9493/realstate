from rest_framework import status
from rest_framework.exceptions import APIException


class InsufficientAmountError(Exception): ...


class InsufficientAmountErrorError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Insufficient funds to complete this transaction."
    default_code = "insufficient_amount"
