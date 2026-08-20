from django.utils import timezone

from .models import ProcessingJob


class ProcessingService:

    def __init__(self, job):
        self.job = job

    def start(self):
        self.job.status = "RUNNING"
        self.job.started_at = timezone.now()
        self.job.error_message = None
        self.job.save(
            update_fields=[
                "status",
                "started_at",
                "error_message",
                "updated_at",
            ]
        )

    def complete(self):
        self.job.status = "COMPLETED"
        self.job.completed_at = timezone.now()
        self.job.save(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )

    def fail_job(self, message):
        self.job.status = "FAILED"
        self.job.error_message = str(message)
        self.job.completed_at = timezone.now()

        self.job.save(
            update_fields=[
                "status",
                "error_message",
                "completed_at",
                "updated_at",
            ]
        )

    def update_progress(
        self,
        completed=None,
        failed=None,
        last_processed_id=None
    ):
        if completed is not None:
            self.job.completed_items = completed

        if failed is not None:
            self.job.failed_items = failed

        if last_processed_id is not None:
            self.job.last_processed_id = last_processed_id

        self.job.save(
            update_fields=[
                "completed_items",
                "failed_items",
                "last_processed_id",
                "updated_at",
            ]
        )

    @property
    def progress_percentage(self):
        if self.job.total_items == 0:
            return 0

        processed = (
            self.job.completed_items +
            self.job.failed_items
        )

        return round(
            (processed / self.job.total_items) * 100,
            2
        )