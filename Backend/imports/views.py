from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle
from django.core.paginator import Paginator, EmptyPage

from common.responses import ApiResponse
from .models import ImportJob
from .serializers import ImportJobSerializer
from .tasks import process_import_task


class ImportUploadView(APIView):
    """
    Handles file upload (throttled at 10/min) and paginated listing (throttled at 120/min).
    """

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]
    throttle_classes = [ScopedRateThrottle]

    def get_throttling_scope(self):
        if self.request.method.lower() == "post":
            return "imports_upload"
        return "imports_read"

    def get(self, request):
        try:
            page_number = int(request.query_params.get("page", 1))
        except (ValueError, TypeError):
            page_number = 1

        try:
            per_page = int(request.query_params.get("perPage", 20))
        except (ValueError, TypeError):
            per_page = 20

        queryset = ImportJob.objects.all().order_by("-id")
        paginator = Paginator(queryset, per_page)
        total_items = paginator.count
        total_pages = paginator.num_pages if total_items > 0 else 1

        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            page_obj = []

        serializer = ImportJobSerializer(
            page_obj,
            many=True,
            context={"request": request},
        )

        pagination_meta = {
            "page": page_number,
            "perPage": per_page,
            "totalItems": total_items,
            "totalPages": total_pages,
            "hasNextPage": page_number < total_pages,
            "hasPrevPage": page_number > 1,
            "nextCursor": None,
        }

        return ApiResponse.success(
            data=serializer.data,
            message="Import jobs fetched successfully.",
            status_code=status.HTTP_200_OK,
            pagination=pagination_meta,
            request=request,
        )

    def post(self, request):
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return ApiResponse.error(
                message="No file uploaded.",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={
                    "expected_field": "file",
                    "received_files": list(request.FILES.keys()),
                    "content_type": request.content_type,
                },
                request=request,
            )

        filename = uploaded_file.name.lower().strip()
        if not (filename.endswith(".xlsx") or filename.endswith(".csv")):
            return ApiResponse.error(
                message="Only CSV and XLSX files are supported.",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={"filename": uploaded_file.name},
                request=request,
            )

        import_job = ImportJob.objects.create(
            file_name=uploaded_file.name,
            file=uploaded_file,
            status="PENDING",
        )

        # Asynchronous processing via Celery
        try:
            process_import_task.delay(import_job.id)
        except Exception:
            # Fallback for standalone dev environments
            from .services import process_import
            process_import(import_job, import_job.file)
            import_job.refresh_from_db()

        serializer = ImportJobSerializer(
            import_job,
            context={"request": request},
        )

        return ApiResponse.success(
            data=serializer.data,
            message="Import job scheduled successfully.",
            status_code=status.HTTP_202_ACCEPTED,
            request=request,
        )


class ImportDetailView(APIView):
    """
    Retrieves status and details of a single import job (throttled at 120/min).
    """

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "imports_read"

    def get(self, request, pk):
        try:
            import_job = ImportJob.objects.get(pk=pk)
        except ImportJob.DoesNotExist:
            return ApiResponse.error(
                message="Import job not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors={"import_id": pk},
                request=request,
            )

        serializer = ImportJobSerializer(
            import_job,
            context={"request": request},
        )

        return ApiResponse.success(
            data=serializer.data,
            message="Import job fetched successfully.",
            status_code=status.HTTP_200_OK,
            request=request,
        )
