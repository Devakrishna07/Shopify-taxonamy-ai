from django.db.models import Q

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    TaxonomyCategory,
    TaxonomyAttribute,
    TaxonomyValue,
    CategoryAttribute,
    ProductTaxonomyResult,
)

from .serializers import (
    TaxonomyCategorySerializer,
    TaxonomyAttributeSerializer,
    TaxonomyValueSerializer,
    CategoryAttributeSerializer,
    ProductTaxonomyResultSerializer,
)

from .services import classify_product

from products.models import Product


# ============================================================
# TAXONOMY CATEGORIES
# ============================================================

class TaxonomyCategoryListAPIView(ListAPIView):
    """
    GET /taxonomy/categories/

    Returns active Shopify taxonomy categories.

    Optional query parameters:

        ?level=1
        ?root=true
        ?leaf=true
        ?search=shirt
    """

    serializer_class = TaxonomyCategorySerializer

    def get_queryset(self):

        queryset = TaxonomyCategory.objects.filter(
            is_archived=False
        )

        level = self.request.query_params.get("level")

        root = self.request.query_params.get("root")

        leaf = self.request.query_params.get("leaf")

        search = self.request.query_params.get("search")

        if level not in [None, ""]:
            try:
                queryset = queryset.filter(
                    level=int(level)
                )
            except (TypeError, ValueError):
                return TaxonomyCategory.objects.none()

        if root == "true":
            queryset = queryset.filter(
                is_root=True
            )

        elif root == "false":
            queryset = queryset.filter(
                is_root=False
            )

        if leaf == "true":
            queryset = queryset.filter(
                is_leaf=True
            )

        elif leaf == "false":
            queryset = queryset.filter(
                is_leaf=False
            )

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                |
                Q(full_name__icontains=search)
                |
                Q(shopify_id__icontains=search)
            )

        return queryset.order_by("full_name")


# ============================================================
# TAXONOMY SEARCH
# ============================================================

class TaxonomySearchAPIView(APIView):
    """
    GET /taxonomy/search/?q=shirt

    Searches Shopify taxonomy categories.
    """

    def get(self, request):

        query = request.query_params.get(
            "q",
            ""
        ).strip()

        if not query:

            return Response(
                {
                    "message": "Search query is required.",
                    "query": "",
                    "count": 0,
                    "results": [],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = (
            TaxonomyCategory.objects
            .filter(
                is_archived=False
            )
            .filter(
                Q(name__icontains=query)
                |
                Q(full_name__icontains=query)
                |
                Q(shopify_id__icontains=query)
            )
            .order_by("full_name")[:50]
        )

        serializer = TaxonomyCategorySerializer(
            queryset,
            many=True
        )

        return Response(
            {
                "query": query,
                "count": len(serializer.data),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# TAXONOMY ATTRIBUTES
# ============================================================

class TaxonomyAttributeListAPIView(ListAPIView):
    """
    GET /taxonomy/attributes/

    Returns all taxonomy attributes.
    """

    serializer_class = TaxonomyAttributeSerializer

    def get_queryset(self):

        queryset = TaxonomyAttribute.objects.all()

        search = self.request.query_params.get(
            "search"
        )

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                |
                Q(description__icontains=search)
                |
                Q(shopify_id__icontains=search)
            )

        return queryset.order_by("name")


# ============================================================
# TAXONOMY VALUES
# ============================================================

class TaxonomyValueListAPIView(ListAPIView):
    """
    GET /taxonomy/values/

    Optional:

        ?attribute=<attribute_id>
        ?search=red
    """

    serializer_class = TaxonomyValueSerializer

    def get_queryset(self):

        queryset = (
            TaxonomyValue.objects
            .select_related("attribute")
            .all()
        )

        attribute_id = self.request.query_params.get(
            "attribute"
        )

        search = self.request.query_params.get(
            "search"
        )

        if attribute_id:
            queryset = queryset.filter(
                attribute_id=attribute_id
            )

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                |
                Q(shopify_id__icontains=search)
            )

        return queryset.order_by("name")


# ============================================================
# CATEGORY ATTRIBUTES
# ============================================================

class CategoryAttributeListAPIView(APIView):
    """
    GET /taxonomy/categories/<category_id>/attributes/

    Returns attributes associated with a category.
    """

    def get(self, request, category_id):

        try:

            category = TaxonomyCategory.objects.get(
                pk=category_id,
                is_archived=False,
            )

        except TaxonomyCategory.DoesNotExist:

            return Response(
                {
                    "message": "Taxonomy category not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        queryset = (
            CategoryAttribute.objects
            .filter(
                category=category
            )
            .select_related("category", "attribute")
            .order_by(
                "-required",
                "attribute__name",
            )
        )

        serializer = CategoryAttributeSerializer(
            queryset,
            many=True
        )

        return Response(
            {
                "category": TaxonomyCategorySerializer(
                    category
                ).data,
                "count": len(serializer.data),
                "attributes": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# PRODUCT TAXONOMY RESULT
# ============================================================

class ProductTaxonomyAPIView(APIView):
    """
    GET /taxonomy/products/<product_id>/

    Returns the taxonomy classification of a product.
    """

    def get(self, request, product_id):

        try:

            result = (
                ProductTaxonomyResult.objects
                .select_related(
                    "product",
                    "category",
                )
                .get(
                    product_id=product_id
                )
            )

        except ProductTaxonomyResult.DoesNotExist:

            return Response(
                {
                    "message": (
                        "Product has not been classified."
                    ),
                    "product_id": product_id,
                    "status": "not_classified",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProductTaxonomyResultSerializer(
            result
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# CLASSIFY SINGLE PRODUCT
# ============================================================

class ClassifyProductAPIView(APIView):
    """
    POST /taxonomy/products/<product_id>/classify/

    Classifies one product using the existing
    taxonomy classification service.
    """

    def post(self, request, product_id):

        try:

            product = Product.objects.get(
                id=product_id
            )

        except Product.DoesNotExist:

            return Response(
                {
                    "message": "Product not found.",
                    "product_id": product_id,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:

            result = classify_product(
                product
            )

        except ValueError as error:

            return Response(
                {
                    "message": str(error),
                    "product_id": product_id,
                    "status": "failed",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as error:

            return Response(
                {
                    "message": (
                        "Product classification failed."
                    ),
                    "error": str(error),
                    "product_id": product_id,
                    "status": "failed",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = ProductTaxonomyResultSerializer(
            result
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# BULK CLASSIFICATION
# ============================================================

class BulkClassifyProductsAPIView(APIView):
    """
    POST /taxonomy/products/classify/

    Optional request body:

        {
            "limit": 10
        }

    If limit is omitted, all products are processed.
    """

    def post(self, request):

        queryset = Product.objects.all().order_by(
            "id"
        )

        limit = request.data.get(
            "limit"
        )

        if limit not in [None, ""]:

            try:

                limit = int(limit)

                if limit <= 0:

                    return Response(
                        {
                            "message": (
                                "limit must be greater than 0."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                queryset = queryset[:limit]

            except (TypeError, ValueError):

                return Response(
                    {
                        "message": (
                            "limit must be a valid integer."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        processed = 0
        classified = 0
        review = 0
        failed = 0

        errors = []

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

            except Exception as error:

                failed += 1

                errors.append(
                    {
                        "product_id": product.id,
                        "error": str(error),
                    }
                )

        return Response(
            {
                "processed": processed,
                "classified": classified,
                "review": review,
                "failed": failed,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )