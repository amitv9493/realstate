from drf_standardized_errors.formatter import ExceptionFormatter
from drf_standardized_errors.handler import exception_handler as drf_standardized_exception_handler
from payment.errors import InsufficientAmountErrorError


def custom_exception_handler(exc, context):
    # Check if it's your custom error
    if isinstance(exc, InsufficientAmountErrorError):
        # Format it as a 400 error
        formatter = ExceptionFormatter(exc, context)
        return formatter.format_error_response()

    # For all other exceptions, use the standardized error handler
    return drf_standardized_exception_handler(exc, context)
