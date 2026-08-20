from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ProcessingJob
from .serializers import ProcessingJobSerializer

from .batch.tasks import process_job


class ProcessingJobListCreateView(
    APIView
):

    def get(
        self,
        request,
    ):

        jobs = ProcessingJob.objects.all()

        serializer = ProcessingJobSerializer(
            jobs,
            many=True,
        )

        return Response(
            serializer.data
        )

    def post(
        self,
        request,
    ):

        job_type = request.data.get(
            "job_type",
            "FULL_PIPELINE",
        )

        import_id = request.data.get(
            "import_id"
        )

        max_retries = request.data.get(
            "max_retries",
            3,
        )

        try:
            max_retries = int(
                max_retries
            )
        except (
            TypeError,
            ValueError,
        ):
            max_retries = 3

        if max_retries < 0:
            max_retries = 0

        job = ProcessingJob.objects.create(
            job_type=job_type,
            import_id=import_id,
            max_retries=max_retries,
        )

        serializer = ProcessingJobSerializer(
            job
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ProcessingJobDetailView(
    APIView
):

    def get(
        self,
        request,
        pk,
    ):

        try:

            job = ProcessingJob.objects.get(
                pk=pk
            )

        except ProcessingJob.DoesNotExist:

            return Response(
                {
                    "detail":
                        "Processing job not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProcessingJobSerializer(
            job
        )

        return Response(
            serializer.data
        )


class ProcessingJobStartView(
    APIView
):

    def post(
        self,
        request,
        pk,
    ):

        try:

            job = ProcessingJob.objects.get(
                pk=pk
            )

        except ProcessingJob.DoesNotExist:

            return Response(
                {
                    "detail":
                        "Processing job not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if job.status == "RUNNING":

            return Response(
                {
                    "detail":
                        "Job is already running."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Optional chunk size.
        chunk_size = request.data.get(
            "chunk_size",
            100,
        )

        try:
            chunk_size = int(
                chunk_size
            )
        except (
            TypeError,
            ValueError,
        ):
            chunk_size = 100

        if chunk_size <= 0:
            chunk_size = 100

        # Execute batch.
        #
        # For the prototype this is synchronous.
        # The same process_job() function can later
        # be dispatched to a worker queue.
        summary = process_job(
            job.id,
            chunk_size=chunk_size,
        )

        job.refresh_from_db()

        serializer = ProcessingJobSerializer(
            job
        )

        return Response(
            {
                "job": serializer.data,
                "summary": summary,
            },
            status=status.HTTP_202_ACCEPTED,
        )