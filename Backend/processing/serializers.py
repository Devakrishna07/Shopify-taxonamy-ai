from rest_framework import serializers

from .models import ProcessingJob


class ProcessingJobSerializer(
    serializers.ModelSerializer
):

    progress = serializers.SerializerMethodField()

    class Meta:
        model = ProcessingJob

        fields = [
            "id",
            "job_type",
            "status",
            "import_id",
            "total_items",
            "completed_items",
            "failed_items",
            "last_processed_id",
            "error_message",
            "progress",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields

    def get_progress(self, obj):

        if obj.total_items == 0:
            return 0

        processed = (
            obj.completed_items +
            obj.failed_items
        )

        return round(
            (processed / obj.total_items) * 100,
            2
        )