from rest_framework import serializers

from .models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "url",
            "status",
            "local_path",
            "error_message",
            "created_at",
        ]


class ProductSerializer(serializers.ModelSerializer):

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
            "normalized_text",
            "status",
            "images",
            "created_at",
            "updated_at",
        ]