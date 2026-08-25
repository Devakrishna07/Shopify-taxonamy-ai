from rest_framework import status

from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
)

from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ImportJob
from .serializers import ImportJobSerializer
from .services import process_import


class ImportUploadView(APIView):

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def get(self, request):
        jobs = ImportJob.objects.all().order_by("-id")[:10]
        return Response(
            ImportJobSerializer(
                jobs,
                many=True,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        uploaded_file = request.FILES.get("file")

        if not uploaded_file:

            return Response(
                {
                    "error": "No file uploaded.",
                    "expected_field": "file",
                    "received_files": list(
                        request.FILES.keys()
                    ),
                    "content_type": request.content_type,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        filename = (
            uploaded_file.name
            .lower()
            .strip()
        )

        if not (
            filename.endswith(".xlsx")
            or filename.endswith(".csv")
        ):

            return Response(
                {
                    "error": (
                        "Only CSV and XLSX files "
                        "are supported."
                    ),
                    "filename": uploaded_file.name,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create the ImportJob and persist the uploaded file.
        import_job = ImportJob.objects.create(
            file_name=uploaded_file.name,
            file=uploaded_file,
            status="PENDING",
        )

        try:

            process_import(
                import_job,
                import_job.file,
            )

            # Refresh in case process_import
            # changed the database record.
            import_job.refresh_from_db()

        except ValueError as error:

            import_job.status = "FAILED"

            import_job.save(
                update_fields=["status"]
            )

            return Response(
                {
                    "import_id": import_job.id,
                    "status": "FAILED",
                    "error": str(error),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as error:

            import_job.status = "FAILED"

            import_job.save(
                update_fields=["status"]
            )

            return Response(
                {
                    "import_id": import_job.id,
                    "status": "FAILED",
                    "error": str(error),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            ImportJobSerializer(
                import_job,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


class ImportDetailView(APIView):

    def get(self, request, pk):

        try:

            import_job = ImportJob.objects.get(
                pk=pk
            )

        except ImportJob.DoesNotExist:

            return Response(
                {
                    "error": "Import job not found.",
                    "import_id": pk,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            ImportJobSerializer(
                import_job,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )