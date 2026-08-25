from rest_framework import serializers

from .models import ReviewAction


class ReviewActionSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.product:
            representation['product_info'] = {
                'id': instance.product.id,
                'title': instance.product.title,
                'images': [{'url': img.url} for img in instance.product.images.all()]
            }
        return representation

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