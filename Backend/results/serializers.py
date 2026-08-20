from rest_framework import serializers

from products.models import Product
from classification.models import ClassificationResult


class ResultProductSerializer(serializers.ModelSerializer):

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
        ]


class ResultSerializer(serializers.ModelSerializer):

    product = ResultProductSerializer(read_only=True)

    class Meta:
        model = ClassificationResult

        fields = [
            "id",
            "product",
            "confidence",
            "status",
        ]