import uuid
from datetime import datetime, timezone
from rest_framework.response import Response
from rest_framework import status


class ApiResponse:
    """
    Standardized API Response Envelope utility.
    """

    @staticmethod
    def _build_meta(request=None, pagination=None):
        request_id = None
        if request and hasattr(request, "headers"):
            request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = f"req_{uuid.uuid4().hex[:16]}"

        meta = {
            "requestId": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if pagination is not None:
            meta["pagination"] = pagination

        return meta

    @classmethod
    def success(
        cls,
        data=None,
        message="Operation successful.",
        status_code=status.HTTP_200_OK,
        pagination=None,
        request=None,
    ):
        payload = {
            "success": True,
            "statusCode": status_code,
            "message": message,
            "data": data,
            "meta": cls._build_meta(request=request, pagination=pagination),
        }
        return Response(payload, status=status_code)

    @classmethod
    def error(
        cls,
        message="An error occurred.",
        status_code=status.HTTP_400_BAD_REQUEST,
        data=None,
        errors=None,
        request=None,
    ):
        payload = {
            "success": False,
            "statusCode": status_code,
            "message": message,
            "data": data if data is not None else errors,
            "meta": cls._build_meta(request=request),
        }
        return Response(payload, status=status_code)
