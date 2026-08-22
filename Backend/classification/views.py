from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from classification.models import ClassificationResult
from classification.serializers import ClassificationResultSerializer
from products.models import Product
from services.classification_service import ClassificationService


class ProductClassificationView(APIView):
    """
    Classify a single product.
    """

    def post(self, request, product_id):
        try:
            Product.objects.get(id=product_id)

            service = ClassificationService()

            result = service.classify_product(product_id)

            serializer = ClassificationResultSerializer(result)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        except Product.DoesNotExist:
            return Response(
                {
                    "error": "Product not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as exc:
            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ClassificationResultView(APIView):
    """
    Return the existing classification result for a product.
    """

    def get(self, request, product_id):
        try:
            result = (
                ClassificationResult.objects
                .select_related(
                    "product",
                    "category",
                )
                .prefetch_related(
                    "product__classification_candidates__category",
                )
                .get(product_id=product_id)
            )

            serializer = ClassificationResultSerializer(result)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        except ClassificationResult.DoesNotExist:
            return Response(
                {
                    "error": "Classification result not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class ImportClassificationView(APIView):
    """
    Classify all products belonging to an import.
    """

    def post(self, request, import_id):
        products = (
            Product.objects
            .filter(import_id=import_id)
            .exclude(status="COMPLETED")
        )

        if not products.exists():
            return Response(
                {
                    "message": "No products available for classification.",
                    "import_id": import_id,
                    "total": 0,
                    "completed": 0,
                    "failed": 0,
                    "errors": [],
                },
                status=status.HTTP_200_OK,
            )

        service = ClassificationService()

        total = products.count()
        completed = 0
        failed = 0
        errors = []

        for product in products.iterator():
            try:
                service.classify_product(product.id)
                completed += 1

            except Exception as exc:
                failed += 1

                product.status = "FAILED"

                product.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

                errors.append(
                    {
                        "product_id": product.id,
                        "error": str(exc),
                    }
                )

        return Response(
            {
                "import_id": import_id,
                "total": total,
                "completed": completed,
                "failed": failed,
                "errors": errors[:20],
            },
            status=status.HTTP_200_OK,
        )