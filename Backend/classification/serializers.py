from rest_framework import serializers

from classification.models import (
    ClassificationResult,
    ClassificationCandidate,
)


class ClassificationCandidateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    category_full_name = serializers.CharField(
        source="category.full_name",
        read_only=True,
    )

    class Meta:
        model = ClassificationCandidate

        fields = [
            "id",
            "category",
            "category_name",
            "category_full_name",
            "score",
            "rank",
            "source",
        ]


class ClassificationResultSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
        allow_null=True,
    )

    category_full_name = serializers.CharField(
        source="category.full_name",
        read_only=True,
        allow_null=True,
    )

    candidates = ClassificationCandidateSerializer(
        source="product.classification_candidates",
        many=True,
        read_only=True,
    )

    class Meta:
        model = ClassificationResult

        fields = [
            "id",
            "product",
            "category",
            "category_name",
            "category_full_name",
            "confidence",
            "text_score",
            "image_score",
            "attribute_score",
            "status",
            "reason",
            "candidates",
            "created_at",
            "updated_at",
        ]