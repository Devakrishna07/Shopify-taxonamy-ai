from django.core.management import call_command

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ProcessingJob
from .serializers import ProcessingJobSerializer


class ProcessingJobListCreateView(APIView):

    def get(self, request):

        jobs = ProcessingJob.objects.all()

        serializer = ProcessingJobSerializer(
            jobs,
            many=True
        )

        return Response(
            serializer.data
        )

    def post(self, request):

        job_type = request.data.get(
            "job_type",
            "FULL_PIPELINE"
        )

        import_id = request.data.get(
            "import_id"
        )

        job = ProcessingJob.objects.create(
            job_type=job_type,
            import_id=import_id,
        )

        serializer = ProcessingJobSerializer(job)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class ProcessingJobDetailView(APIView):

    def get(self, request, pk):

        try:
            job = ProcessingJob.objects.get(
                pk=pk
            )
        except ProcessingJob.DoesNotExist:

            return Response(
                {
                    "detail": "Processing job not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProcessingJobSerializer(job)

        return Response(
            serializer.data
        )


class ProcessingJobStartView(APIView):

    def post(self, request, pk):

        try:
            job = ProcessingJob.objects.get(
                pk=pk
            )
        except ProcessingJob.DoesNotExist:

            return Response(
                {
                    "detail": "Processing job not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if job.status == "RUNNING":

            return Response(
                {
                    "detail": "Job is already running."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        job.status = "PENDING"
        job.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        serializer = ProcessingJobSerializer(job)

        return Response(
            serializer.data,
            status=status.HTTP_202_ACCEPTED
        )