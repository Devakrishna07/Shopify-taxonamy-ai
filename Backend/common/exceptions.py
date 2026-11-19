from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled
from rest_framework import status
from .responses import ApiResponse


def standard_exception_handler(exc, context):
    """
    Custom exception handler to wrap DRF exceptions (including 429 Throttling)
    into the standard ApiResponse envelope.
    """
    response = exception_handler(exc, context)

    if response is not None:
        request = context.get("request")
        status_code = response.status_code

        if isinstance(exc, Throttled):
            wait_seconds = int(exc.wait) if exc.wait is not None else 60
            message = (
                f"Request was throttled. Expected available in {wait_seconds} seconds."
            )
            return ApiResponse.error(
                message=message,
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                errors={
                    "available_in_seconds": wait_seconds,
                    "detail": str(exc.detail),
                },
                request=request,
            )

        # Other standard DRF exceptions
        message = (
            response.data.get("detail", "An error occurred.")
            if isinstance(response.data, dict)
            else "Validation error."
        )

        return ApiResponse.error(
            message=str(message),
            status_code=status_code,
            errors=response.data,
            request=request,
        )

    return response

