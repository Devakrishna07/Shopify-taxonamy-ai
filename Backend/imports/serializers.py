from rest_framework import serializers

from .models import ImportJob, ImportRowError


class ImportJobSerializer(serializers.ModelSerializer):

    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ImportJob

        fields = [
            "id",
            "file_name",
            "file",
            "file_url",
            "status",
            "total_rows",
            "processed_rows",
            "failed_rows",
            "created_at",
            "completed_at",
        ]

        read_only_fields = [
            "id",
            "file_name",
            "file_url",
            "status",
            "total_rows",
            "processed_rows",
            "failed_rows",
            "created_at",
            "completed_at",
        ]

    def get_file_url(self, obj):
        request = self.context.get("request")

        if not obj.file:
            return None

        url = obj.file.url

        if request:
            return request.build_absolute_uri(url)

        return url


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