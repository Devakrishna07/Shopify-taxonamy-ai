from rest_framework import serializers

from .models import (
    TaxonomyCategory,
    TaxonomyAttribute,
    TaxonomyValue,
    CategoryAttribute,
    ProductTaxonomyResult,
)


# ============================================================
# CATEGORY
# ============================================================

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
            "created_at",
            "updated_at",
        ]


# ============================================================
# ATTRIBUTE
# ============================================================

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
            "created_at",
        ]


# ============================================================
# VALUE
# ============================================================

class TaxonomyValueSerializer(
    serializers.ModelSerializer
):

    attribute_name = serializers.CharField(
        source="attribute.name",
        read_only=True,
    )

    class Meta:

        model = TaxonomyValue

        fields = [
            "id",
            "shopify_id",
            "attribute",
            "attribute_name",
            "name",
            "created_at",
        ]


# ============================================================
# CATEGORY ATTRIBUTE
# ============================================================

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


# ============================================================
# PRODUCT TAXONOMY RESULT
# ============================================================

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