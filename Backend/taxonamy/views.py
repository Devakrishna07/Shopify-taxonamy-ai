from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from .models import (
    TaxonomyCategory,
    ProductTaxonomyResult,
)

from .serializers import (
    TaxonomyCategorySerializer,
    ProductTaxonomyResultSerializer,
)

from .services import classify_product

from products.models import Product


class TaxonomyCategoryListAPIView(
    ListAPIView
):

    serializer_class = TaxonomyCategorySerializer

    def get_queryset(self):

        queryset = TaxonomyCategory.objects.filter(
            is_archived=False
        )

        level = self.request.query_params.get(
            "level"
        )

        root = self.request.query_params.get(
            "root"
        )

        if level:
            queryset = queryset.filter(
                level=level
            )

        if root == "true":
            queryset = queryset.filter(
                is_root=True
            )

        return queryset


class TaxonomySearchAPIView(
    APIView
):

    def get(self, request):

        query = request.query_params.get(
            "q",
            ""
        ).strip()

        if not query:

            return Response({
                "message": "Search query is required.",
                "results": []
            })

        queryset = TaxonomyCategory.objects.filter(
            Q(name__icontains=query)
            |
            Q(full_name__icontains=query),
            is_archived=False
        )[:50]

        serializer = TaxonomyCategorySerializer(
            queryset,
            many=True
        )

        return Response({
            "query": query,
            "count": len(serializer.data),
            "results": serializer.data
        })


class ProductTaxonomyAPIView(
    APIView
):

    def get(self, request, product_id):

        try:

            result = ProductTaxonomyResult.objects.select_related(
                "category"
            ).get(
                product_id=product_id
            )

        except ProductTaxonomyResult.DoesNotExist:

            return Response(
                {
                    "message": "Product has not been classified."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductTaxonomyResultSerializer(
            result
        )

        return Response(
            serializer.data
        )


class ClassifyProductAPIView(
    APIView
):

    def post(self, request, product_id):

        try:

            product = Product.objects.get(
                id=product_id
            )

        except Product.DoesNotExist:

            return Response(
                {
                    "message": "Product not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        result = classify_product(
            product
        )

        serializer = ProductTaxonomyResultSerializer(
            result
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class BulkClassifyProductsAPIView(
    APIView
):

    def post(self, request):

        queryset = Product.objects.all()

        limit = request.data.get(
            "limit"
        )

        if limit:

            queryset = queryset[:int(limit)]

        processed = 0
        classified = 0
        review = 0
        failed = 0

        for product in queryset:

            try:

                result = classify_product(
                    product
                )

                processed += 1

                if result.status == "classified":
                    classified += 1

                elif result.status == "review":
                    review += 1

            except Exception:

                failed += 1

        return Response({
            "processed": processed,
            "classified": classified,
            "review": review,
            "failed": failed,
        })

    