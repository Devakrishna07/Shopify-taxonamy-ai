from rest_framework import serializers

from .models import TaxonomyCategory


class TaxonomyCategorySerializer(serializers.ModelSerializer):

    parent_name = serializers.CharField(
        source="parent.name",
        read_only=True
    )

    class Meta:
        model = TaxonomyCategory
        fields = [
            "id",
            "shopify_id",
            "name",
            "full_name",
            "parent",
            "parent_name",
            "level",
            "is_leaf",
            "taxonomy_version",
        ]