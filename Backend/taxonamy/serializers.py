from rest_framework import serializers

from .models import (
    TaxonomyCategory,
    TaxonomyAttribute,
    TaxonomyValue,
    CategoryAttribute,
    ProductTaxonomyResult,
)


class TaxonomyCategorySerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = TaxonomyCategory
        fields = [
            "id",
            "shopify_id",
            "name",
            "full_name",
            "parent_id",
            "level",
            "is_root",
            "is_leaf",
            "is_archived",
        ]


class TaxonomyAttributeSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = TaxonomyAttribute
        fields = [
            "id",
            "shopify_id",
            "name",
            "description",
        ]


class TaxonomyValueSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = TaxonomyValue
        fields = [
            "id",
            "shopify_id",
            "attribute",
            "name",
        ]


class CategoryAttributeSerializer(
    serializers.ModelSerializer
):
    attribute = TaxonomyAttributeSerializer(
        read_only=True
    )

    class Meta:
        model = CategoryAttribute
        fields = [
            "id",
            "category",
            "attribute",
            "required",
        ]


class ProductTaxonomyResultSerializer(
    serializers.ModelSerializer
):
    category = TaxonomyCategorySerializer(
        read_only=True
    )

    class Meta:
        model = ProductTaxonomyResult
        fields = [
            "id",
            "product",
            "category",
            "confidence",
            "matched_text",
            "status",
            "created_at",
            "updated_at",
        ]