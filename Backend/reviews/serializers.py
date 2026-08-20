from rest_framework import serializers

from .models import ReviewAction


class ReviewActionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReviewAction
        fields = [
            "id",
            "product",
            "old_category_id",
            "new_category_id",
            "action",
            "comment",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]