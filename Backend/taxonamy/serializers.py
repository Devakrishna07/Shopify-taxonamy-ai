from rest_framework import serializers

from .models import (
    TaxonomyCategory,
    TaxonomyAttribute,
    TaxonomyValue,
    CategoryAttribute,
    ProductTaxonomyResult,
)


class TaxonomyCategorySerializer(serializers.ModelSerializer):
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
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class TaxonomyAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxonomyAttribute
        fields = [
            "id",
            "shopify_id",
            "name",
            "description",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class TaxonomyValueSerializer(serializers.ModelSerializer):
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
        read_only_fields = [
            "id",
            "attribute_name",
            "created_at",
        ]


class CategoryAttributeSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(
        source="attribute.name",
        read_only=True,
    )

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    class Meta:
        model = CategoryAttribute
        fields = [
            "id",
            "category",
            "category_name",
            "attribute",
            "attribute_name",
            "required",
        ]
        read_only_fields = [
            "id",
            "category_name",
            "attribute_name",
        ]


class ProductTaxonomyResultSerializer(
    serializers.ModelSerializer
):
    product_title = serializers.SerializerMethodField()
    product_sku = serializers.SerializerMethodField()
    product_external_id = serializers.SerializerMethodField()

    category_id = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    category_full_name = serializers.SerializerMethodField()
    category_level = serializers.SerializerMethodField()

    class Meta:
        model = ProductTaxonomyResult
        fields = [
            "id",
            "product",
            "category",
            "product_title",
            "product_sku",
            "product_external_id",
            "category_id",
            "category_name",
            "category_full_name",
            "category_level",
            "confidence",
            "matched_text",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "product_title",
            "product_sku",
            "product_external_id",
            "category_id",
            "category_name",
            "category_full_name",
            "category_level",
            "created_at",
            "updated_at",
        ]

    def get_product_title(self, obj):
        if not obj.product:
            return None

        return getattr(
            obj.product,
            "title",
            None,
        )

    def get_product_sku(self, obj):
        if not obj.product:
            return None

        return getattr(
            obj.product,
            "sku",
            None,
        )

    def get_product_external_id(self, obj):
        if not obj.product:
            return None

        return getattr(
            obj.product,
            "external_product_id",
            None,
        )

    def get_category_id(self, obj):
        if not obj.category:
            return None

        return obj.category.id

    def get_category_name(self, obj):
        if not obj.category:
            return None

        return getattr(
            obj.category,
            "name",
            None,
        )

    def get_category_full_name(self, obj):
        if not obj.category:
            return None

        return getattr(
            obj.category,
            "full_name",
            None,
        )

    def get_category_level(self, obj):
        if not obj.category:
            return None

        return getattr(
            obj.category,
            "level",
            None,
        )