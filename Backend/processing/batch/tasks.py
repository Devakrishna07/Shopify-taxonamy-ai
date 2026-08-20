from processing.models import ProcessingJob

from .processor import BatchProcessor


def process_job(
    job_id,
    chunk_size=100,
):
    """
    Execute a ProcessingJob.

    This function can later be connected to
    Celery, RQ, Django-Q, or another worker
    without changing BatchProcessor.
    """

    job = ProcessingJob.objects.get(
        pk=job_id
    )

    processor = BatchProcessor(
        job=job,
        chunk_size=chunk_size,
    )

    return processor.run()