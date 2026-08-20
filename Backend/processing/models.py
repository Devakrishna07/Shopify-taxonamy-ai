from django.db import models


class ProcessingJob(models.Model):

    JOB_TYPES = [
        ("IMPORT", "Import"),
        ("CLASSIFY", "Classify"),
        ("IMAGE", "Image"),
        ("ATTRIBUTE", "Attribute"),
        ("FULL_PIPELINE", "Full Pipeline"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    job_type = models.CharField(
        max_length=50,
        choices=JOB_TYPES
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    # Optional source import.
    import_id = models.BigIntegerField(
        null=True,
        blank=True
    )

    # Batch statistics.
    total_items = models.PositiveIntegerField(
        default=0
    )

    completed_items = models.PositiveIntegerField(
        default=0
    )

    failed_items = models.PositiveIntegerField(
        default=0
    )

    # Last successfully or unsuccessfully attempted product.
    last_processed_id = models.BigIntegerField(
        null=True,
        blank=True
    )

    # Retry configuration.
    max_retries = models.PositiveIntegerField(
        default=3
    )

    retry_count = models.PositiveIntegerField(
        default=0
    )

    # Last batch error.
    error_message = models.TextField(
        null=True,
        blank=True
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "processing_jobs"

        ordering = [
            "-created_at"
        ]

        indexes = [
            models.Index(
                fields=["status"]
            ),
            models.Index(
                fields=["job_type"]
            ),
            models.Index(
                fields=["import_id"]
            ),
        ]

    def __str__(self):
        return (
            f"Job {self.id} - "
            f"{self.job_type} - "
            f"{self.status}"
        )