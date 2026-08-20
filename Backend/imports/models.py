from django.db import models


class ImportJob(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    file_name = models.CharField(max_length=255)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    total_rows = models.PositiveIntegerField(default=0)

    processed_rows = models.PositiveIntegerField(default=0)

    failed_rows = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.file_name} - {self.status}"

    # row level failure tracking
class ImportRowError(models.Model):

    import_job = models.ForeignKey(
        ImportJob,
        on_delete=models.CASCADE,
        related_name="row_errors"
    )

    row_number = models.PositiveIntegerField()

    error_message = models.TextField()

    raw_data = models.JSONField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Row {self.row_number} - Import {self.import_job_id}"