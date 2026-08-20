from rest_framework import serializers

from .models import ProductAttribute


class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(
        source='attribute.name',
        read_only=True
    )

    value_name = serializers.CharField(
        source='value.value',
        read_only=True
    )

    class Meta:
        model = ProductAttribute
        fields = [
            'id',
            'product',
            'attribute',
            'attribute_name',
            'value',
            'value_name',
            'raw_value',
            'confidence',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'attribute_name',
            'value_name',
            'created_at',
            'updated_at',
        ]