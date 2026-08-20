from rest_framework import serializers

from .models import ImportJob, ImportRowError


class ImportJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImportJob
        fields = [
            "id",
            "file_name",
            "status",
            "total_rows",
            "processed_rows",
            "failed_rows",
            "created_at",
            "completed_at",
        ]


class ImportRowErrorSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImportRowError
        fields = [
            "id",
            "row_number",
            "error_message",
            "raw_data",
            "created_at",
        ]