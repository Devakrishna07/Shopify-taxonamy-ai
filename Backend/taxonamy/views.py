
from django.db.models import Q, Count
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

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

from .services import (
    classify_product,
    build_category_index,
)


# ============================================================
# TAXONOMY CATEGORY APIs
# ============================================================


class TaxonomyCategoryListAPIView(ListAPIView):
    serializer_class = TaxonomyCategorySerializer

    def get_queryset(self):
        queryset = (
            TaxonomyCategory.objects
            .filter(
                is_archived=False,
            )
            .order_by("full_name")
        )

        level = self.request.query_params.get(
            "level"
        )

        root = self.request.query_params.get(
            "root"
        )

        leaf = self.request.query_params.get(
            "leaf"
        )

        search = self.request.query_params.get(
            "search"
        )

        if level not in [None, ""]:
            try:
                queryset = queryset.filter(
                    level=int(level)
                )
            except (
                TypeError,
                ValueError,
            ):
                return queryset.none()

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
                | Q(
                    full_name__icontains=search
                )
                | Q(
                    shopify_id__icontains=search
                )
            )

        return queryset


class TaxonomySearchAPIView(APIView):
    def get(self, request):
        query = request.query_params.get(
            "q",
            "",
        ).strip()

        if not query:
            return Response(
                {
                    "query": "",
                    "count": 0,
                    "results": [],
                }
            )

        queryset = (
            TaxonomyCategory.objects
            .filter(
                is_archived=False,
            )
            .filter(
                Q(name__icontains=query)
                | Q(
                    full_name__icontains=query
                )
                | Q(
                    shopify_id__icontains=query
                )
            )
            .order_by(
                "full_name"
            )[:50]
        )

        data = TaxonomyCategorySerializer(
            queryset,
            many=True,
        ).data

        return Response(
            {
                "query": query,
                "count": len(data),
                "results": data,
            }
        )


# ============================================================
# ATTRIBUTE APIs
# ============================================================


class TaxonomyAttributeListAPIView(
    ListAPIView
):
    serializer_class = (
        TaxonomyAttributeSerializer
    )

    def get_queryset(self):
        queryset = (
            TaxonomyAttribute.objects
            .all()
            .order_by("name")
        )

        search = (
            self.request.query_params.get(
                "search"
            )
        )

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(
                    description__icontains=search
                )
                | Q(
                    shopify_id__icontains=search
                )
            )

        return queryset


class TaxonomyValueListAPIView(
    ListAPIView
):
    serializer_class = (
        TaxonomyValueSerializer
    )

    def get_queryset(self):
        queryset = (
            TaxonomyValue.objects
            .select_related(
                "attribute",
            )
            .all()
            .order_by("name")
        )

        attribute = (
            self.request.query_params.get(
                "attribute"
            )
        )

        search = (
            self.request.query_params.get(
                "search"
            )
        )

        if attribute:
            queryset = queryset.filter(
                attribute_id=attribute
            )

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(
                    shopify_id__icontains=search
                )
            )

        return queryset


class CategoryAttributeListAPIView(
    APIView
):
    def get(
        self,
        request,
        category_id,
    ):
        try:
            category = (
                TaxonomyCategory.objects
                .get(
                    id=category_id,
                    is_archived=False,
                )
            )

        except TaxonomyCategory.DoesNotExist:
            return Response(
                {
                    "message": (
                        "Taxonomy category "
                        "not found."
                    )
                },
                status=404,
            )

        queryset = (
            CategoryAttribute.objects
            .filter(
                category=category,
            )
            .select_related(
                "category",
                "attribute",
            )
            .order_by(
                "-required",
                "attribute__name",
            )
        )

        return Response(
            {
                "category":
                    TaxonomyCategorySerializer(
                        category
                    ).data,

                "count":
                    queryset.count(),

                "attributes":
                    CategoryAttributeSerializer(
                        queryset,
                        many=True,
                    ).data,
            }
        )


# ============================================================
# CLASSIFICATION LIST
# ============================================================


class ProductTaxonomyListAPIView(
    ListAPIView
):
    serializer_class = (
        ProductTaxonomyResultSerializer
    )

    def get_queryset(self):
        queryset = (
            ProductTaxonomyResult.objects
            .select_related(
                "product",
                "category",
            )
            .order_by(
                "-updated_at"
            )
        )

        search = (
            self.request.query_params.get(
                "search",
                "",
            ).strip()
        )

        status_value = (
            self.request.query_params.get(
                "status",
                "",
            ).strip()
        )

        classification = (
            self.request.query_params.get(
                "classification",
                "",
            ).strip()
        )

        category = (
            self.request.query_params.get(
                "category",
                "",
            ).strip()
        )

        level = (
            self.request.query_params.get(
                "level",
                "",
            ).strip()
        )

        if search:
            queryset = queryset.filter(
                Q(
                    product__title__icontains=search
                )
                | Q(
                    product__sku__icontains=search
                )
                | Q(
                    product__external_product_id__icontains=search
                )
                | Q(
                    category__name__icontains=search
                )
                | Q(
                    category__full_name__icontains=search
                )
            )

        if status_value:
            queryset = queryset.filter(
                status=status_value
            )

        if classification == "classified":
            queryset = queryset.filter(
                category__isnull=False
            )

        elif classification == "unclassified":
            queryset = queryset.filter(
                category__isnull=True
            )

        if category:
            try:
                queryset = queryset.filter(
                    category_id=int(category)
                )
            except (
                TypeError,
                ValueError,
            ):
                return queryset.none()

        if level:
            try:
                queryset = queryset.filter(
                    category__level=int(level)
                )
            except (
                TypeError,
                ValueError,
            ):
                return queryset.none()

        return queryset


# ============================================================
# SINGLE PRODUCT RESULT
# ============================================================


class ProductTaxonomyAPIView(APIView):
    def get(
        self,
        request,
        product_id,
    ):
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
                        "Product has not "
                        "been classified."
                    ),
                    "product_id": product_id,
                    "status": "not_classified",
                },
                status=404,
            )

        return Response(
            ProductTaxonomyResultSerializer(
                result
            ).data
        )


# ============================================================
# SINGLE CLASSIFICATION
# ============================================================


class ClassifyProductAPIView(APIView):
    def post(
        self,
        request,
        product_id,
    ):
        try:
            product = Product.objects.get(
                id=product_id
            )

        except Product.DoesNotExist:
            return Response(
                {
                    "message": (
                        "Product not found."
                    ),
                    "product_id": product_id,
                },
                status=404,
            )

        try:
            (
                category_map,
                category_index,
            ) = build_category_index()

            result = classify_product(
                product,
                category_map,
                category_index,
            )

            return Response(
                ProductTaxonomyResultSerializer(
                    result
                ).data
            )

        except Exception as error:
            return Response(
                {
                    "message": (
                        "Classification failed."
                    ),
                    "product_id": product_id,
                    "error": str(error),
                    "status": "failed",
                },
                status=500,
            )


# ============================================================
# BULK CLASSIFICATION
# ============================================================


class BulkClassifyProductsAPIView(APIView):
    """
    Process products in safe batches.

    Frontend should repeatedly call this endpoint until
    remaining == 0.

    Default batch = 10.
    Maximum batch = 25.

    This avoids trying to classify 10,000 products inside
    a single HTTP request.
    """

    MAX_BATCH_SIZE = 25

    def post(self, request):
        try:
            limit = int(
                request.data.get(
                    "limit",
                    10,
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            return Response(
                {
                    "message": (
                        "limit must be an integer."
                    )
                },
                status=400,
            )

        limit = max(
            1,
            min(
                limit,
                self.MAX_BATCH_SIZE,
            ),
        )

        only_unclassified = request.data.get(
            "only_unclassified",
            True,
        )

        if isinstance(
            only_unclassified,
            str,
        ):
            only_unclassified = (
                only_unclassified.lower()
                in (
                    "true",
                    "1",
                    "yes",
                )
            )

        queryset = (
            Product.objects
            .all()
            .order_by("id")
        )

        if only_unclassified:
            queryset = queryset.filter(
                taxonomy_result__isnull=True
            )

        products = queryset[:limit]

        (
            category_map,
            category_index,
        ) = build_category_index()

        processed = 0
        classified = 0
        needs_review = 0
        manual_review = 0
        failed = 0

        results = []
        errors = []

        for product in products:
            processed += 1

            try:
                result = classify_product(
                    product,
                    category_map,
                    category_index,
                )

                if result.status == "classified":
                    classified += 1

                elif result.status == "needs_review":
                    needs_review += 1

                elif result.status == "manual_review":
                    manual_review += 1

                elif result.status == "failed":
                    failed += 1

                results.append(
                    {
                        "product_id": product.id,
                        "category_id":
                            result.category_id,
                        "confidence":
                            result.confidence,
                        "status":
                            result.status,
                    }
                )

            except Exception as error:
                failed += 1

                ProductTaxonomyResult.objects.update_or_create(
                    product=product,
                    defaults={
                        "category": None,
                        "confidence": 0,
                        "matched_text": "",
                        "alternatives": [],
                        "attributes": [],
                        "image_status":
                            "not_available",
                        "status": "failed",
                        "review_reason":
                            "Unexpected classification error.",
                        "error_message":
                            str(error),
                        "ai_reason": "",
                    },
                )

                errors.append(
                    {
                        "product_id":
                            product.id,
                        "error":
                            str(error),
                    }
                )

        remaining = (
            Product.objects
            .filter(
                taxonomy_result__isnull=True
            )
            .count()
        )

        return Response(
            {
                "processed": processed,
                "classified": classified,
                "needs_review": needs_review,
                "manual_review": manual_review,
                "failed": failed,
                "remaining": remaining,
                "has_more": remaining > 0,
                "results": results,
                "errors": errors,
            }
        )


# ============================================================
# STATISTICS
# ============================================================


class TaxonomyStatsAPIView(APIView):
    def get(self, request):
        total_products = Product.objects.count()

        result_queryset = (
            ProductTaxonomyResult.objects.all()
        )

        classified = (
            result_queryset
            .filter(
                status="classified"
            )
            .count()
        )

        approved = (
            result_queryset
            .filter(
                status="approved"
            )
            .count()
        )

        needs_review = (
            result_queryset
            .filter(
                status="needs_review"
            )
            .count()
        )

        manual_review = (
            result_queryset
            .filter(
                status="manual_review"
            )
            .count()
        )

        failed = (
            result_queryset
            .filter(
                status="failed"
            )
            .count()
        )

        rejected = (
            result_queryset
            .filter(
                status="rejected"
            )
            .count()
        )

        classified_or_approved = (
            result_queryset
            .filter(
                status__in=[
                    "classified",
                    "approved",
                ]
            )
            .count()
        )

        unclassified = max(
            0,
            total_products
            - result_queryset.count(),
        )

        return Response(
            {
                "total_products":
                    total_products,

                "classified":
                    classified,

                "approved":
                    approved,

                "needs_review":
                    needs_review,

                "manual_review":
                    manual_review,

                "failed":
                    failed,

                "rejected":
                    rejected,

                "classified_or_approved":
                    classified_or_approved,

                "unclassified":
                    unclassified,

                "classification_progress":
                    round(
                        (
                            (
                                result_queryset.count()
                                / total_products
                            )
                            * 100
                        )
                        if total_products
                        else 0,
                        2,
                    ),
            }
        )


# ============================================================
# APPROVE
# ============================================================


class ApproveProductTaxonomyAPIView(
    APIView
):
    def post(
        self,
        request,
        product_id,
    ):
        category_id = request.data.get(
            "category_id"
        )

        if not category_id:
            return Response(
                {
                    "message": (
                        "category_id is required."
                    )
                },
                status=400,
            )

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
                        "Classification result "
                        "not found."
                    )
                },
                status=404,
            )

        try:
            category = (
                TaxonomyCategory.objects
                .get(
                    id=category_id,
                    is_archived=False,
                )
            )

        except TaxonomyCategory.DoesNotExist:
            return Response(
                {
                    "message": (
                        "Taxonomy category "
                        "not found."
                    )
                },
                status=404,
            )

        result.category = category
        result.status = "approved"
        result.review_reason = ""
        result.error_message = ""

        result.save()

        return Response(
            ProductTaxonomyResultSerializer(
                result
            ).data
        )


# ============================================================
# REJECT
# ============================================================


class RejectProductTaxonomyAPIView(
    APIView
):
    def post(
        self,
        request,
        product_id,
    ):
        try:
            result = (
                ProductTaxonomyResult.objects
                .get(
                    product_id=product_id
                )
            )

        except ProductTaxonomyResult.DoesNotExist:
            return Response(
                {
                    "message": (
                        "Classification result "
                        "not found."
                    )
                },
                status=404,
            )

        reason = request.data.get(
            "reason",
            "Classification rejected.",
        )

        result.status = "rejected"
        result.review_reason = reason

        result.save()

        return Response(
            ProductTaxonomyResultSerializer(
                result
            ).data
        )
