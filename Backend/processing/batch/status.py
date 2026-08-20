from django.utils import timezone


class BatchStatusManager:
    """
    Handles ProcessingJob state and progress updates.
    """

    @staticmethod
    def start(job):
        job.status = "RUNNING"

        if job.started_at is None:
            job.started_at = timezone.now()

        job.error_message = None

        job.save(
            update_fields=[
                "status",
                "started_at",
                "error_message",
                "updated_at",
            ]
        )

        return job

    @staticmethod
    def mark_success(
        job,
        product_id,
    ):
        job.completed_items += 1
        job.last_processed_id = product_id

        job.save(
            update_fields=[
                "completed_items",
                "last_processed_id",
                "updated_at",
            ]
        )

    @staticmethod
    def mark_failure(
        job,
        product_id,
        error,
    ):
        job.failed_items += 1
        job.last_processed_id = product_id
        job.error_message = str(error)

        job.save(
            update_fields=[
                "failed_items",
                "last_processed_id",
                "error_message",
                "updated_at",
            ]
        )

    @staticmethod
    def increment_retry(job):
        job.retry_count += 1

        job.save(
            update_fields=[
                "retry_count",
                "updated_at",
            ]
        )

    @staticmethod
    def complete(job):
        job.status = "COMPLETED"
        job.completed_at = timezone.now()

        job.save(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )

    @staticmethod
    def fail(job, error):
        job.status = "FAILED"
        job.error_message = str(error)
        job.completed_at = timezone.now()

        job.save(
            update_fields=[
                "status",
                "error_message",
                "completed_at",
                "updated_at",
            ]
        )

    @staticmethod
    def progress(job):
        if job.total_items == 0:
            return 0

        processed = (
            job.completed_items
            + job.failed_items
        )

        return round(
            (
                processed
                / job.total_items
            ) * 100,
            2,
        )

    @staticmethod
    def is_complete(job):
        processed = (
            job.completed_items
            + job.failed_items
        )

        return processed >= job.total_items