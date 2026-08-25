from rest_framework import serializers

from products.models import Product
from products.serializers import ProductImageSerializer
from classification.models import ClassificationResult

from .models import DecisionReview


class ResultProductSerializer(
    serializers.ModelSerializer
):
    images = ProductImageSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Product

        fields = [
            "id",
            "external_product_id",
            "sku",
            "title",
            "description",
            "brand",
            "product_type",
            "existing_category",
            "existing_subcategory",
            "status",
            "images",
        ]


class DecisionReviewSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = DecisionReview

        fields = [
            "id",
            "ai_prediction",
            "ai_confidence",
            "ai_alternatives",
            "decision_status",
            "requires_review",
            "decision_reason",
            "final_category_id",
            "review_action",
            "approved_by",
            "approved_at",
            "review_comment",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "ai_prediction",
            "ai_confidence",
            "ai_alternatives",
            "decision_status",
            "requires_review",
            "decision_reason",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
        ]


class ResultSerializer(
    serializers.ModelSerializer
):

    product = ResultProductSerializer(
        read_only=True
    )

    decision = serializers.SerializerMethodField()

    class Meta:
        model = ClassificationResult

        fields = [
            "id",
            "product",
            "confidence",
            "status",
            "decision",
        ]

    def get_decision(self, obj):

        decision = getattr(
            obj,
            "decision_review",
            None,
        )

        if not decision:
            return None

        return DecisionReviewSerializer(
            decision
        ).data