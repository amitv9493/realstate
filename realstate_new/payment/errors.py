from rest_framework import status
from rest_framework.exceptions import APIException


class InsufficientAmountError(APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = "Insufficient funds to complete this transaction."
    default_code = "insufficient_amount"
