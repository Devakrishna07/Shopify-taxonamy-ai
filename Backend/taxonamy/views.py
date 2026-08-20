from django.db.models import Q

from rest_framework import generics

from .models import TaxonomyCategory
from .serializers import TaxonomyCategorySerializer


class TaxonomySearchView(generics.ListAPIView):
    serializer_class = TaxonomyCategorySerializer

    def get_queryset(self):
        query = self.request.query_params.get("q", "").strip()

        queryset = TaxonomyCategory.objects.all()

        if not query:
            return queryset.none()

        return queryset.filter(
            Q(name__icontains=query)
            | Q(full_name__icontains=query)
            | Q(shopify_id__icontains=query)
        ).order_by(
            "level",
            "name"
        )