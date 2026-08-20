from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
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

    def post(self, request):

        # DEBUG
        print("================================")
        print("REQUEST CONTENT TYPE:")
        print(request.content_type)

        print("REQUEST FILES:")
        print(request.FILES)

        print("REQUEST DATA:")
        print(request.data)

        print("================================")

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

        filename = uploaded_file.name.lower()

        if not (
            filename.endswith(".xlsx")
            or filename.endswith(".csv")
        ):

            return Response(
                {
                    "error": (
                        "Only CSV and XLSX files "
                        "are supported."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        import_job = ImportJob.objects.create(
            file_name=uploaded_file.name,
            status="PENDING",
        )

        try:

            process_import(
                import_job,
                uploaded_file,
            )

        except Exception as error:

            return Response(
                {
                    "import_id": import_job.id,
                    "status": "FAILED",
                    "error": str(error),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            ImportJobSerializer(import_job).data,
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
                    "error": "Import job not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            ImportJobSerializer(import_job).data
        )