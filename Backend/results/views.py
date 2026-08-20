from django.db.models import Avg, Count
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter

from classification.models import ClassificationResult
from .serializers import ResultSerializer
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from classification.models import ClassificationResult

from .models import DecisionReview
from .serializers import ResultSerializer


class ResultsListView(generics.ListAPIView):
    """
    Return classification results for all processed products.
    """

    serializer_class = ResultSerializer

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "product__title",
        "product__sku",
        "product__brand",
        "product__product_type",
    ]

    ordering_fields = [
        "id",
        "confidence",
    ]

    ordering = [
        "-id"
    ]

    def get_queryset(self):

        queryset = (
            ClassificationResult.objects
            .select_related("product")
            .all()
        )

        status = self.request.query_params.get("status")

        if status:
            queryset = queryset.filter(
                status__iexact=status
            )

        min_confidence = self.request.query_params.get(
            "min_confidence"
        )

        if min_confidence:

            try:
                min_confidence = float(min_confidence)

                queryset = queryset.filter(
                    confidence__gte=min_confidence
                )

            except ValueError:
                pass

        return queryset


class ResultDetailView(generics.RetrieveAPIView):
    """
    Return one classification result.
    """

    queryset = (
        ClassificationResult.objects
        .select_related("product")
        .all()
    )

    serializer_class = ResultSerializer


class ProductResultView(generics.RetrieveAPIView):
    """
    Return the classification result for one product.
    """

    serializer_class = ResultSerializer

    lookup_url_kwarg = "product_id"

    def get_queryset(self):

        return (
            ClassificationResult.objects
            .select_related("product")
            .filter(
                product_id=self.kwargs["product_id"]
            )
        )


class ResultsSummaryView(APIView):
    """
    Dashboard summary of classification results.
    """

    def get(self, request):

        queryset = ClassificationResult.objects.all()

        total = queryset.count()

        high = queryset.filter(
            status__iexact="HIGH"
        ).count()

        review = queryset.filter(
            status__iexact="REVIEW"
        ).count()

        manual = queryset.filter(
            status__iexact="MANUAL_REVIEW"
        ).count()

        failed = queryset.filter(
            status__iexact="FAILED"
        ).count()

        average_confidence = queryset.aggregate(
            average=Avg("confidence")
        )["average"]

        return Response({
            "total_results": total,
            "high_confidence": high,
            "review_required": review,
            "manual_review": manual,
            "failed": failed,
            "average_confidence": average_confidence,
        })

class ResultApproveView(APIView):

    def post(self, request, pk):

        result = (
            ClassificationResult.objects
            .select_related("product")
            .filter(pk=pk)
            .first()
        )

        if not result:
            return Response(
                {"detail": "Result not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        decision = getattr(
            result,
            "decision_review",
            None,
        )

        if not decision:
            return Response(
                {
                    "detail": (
                        "Decision record not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        decision.review_action = (
            DecisionReview.APPROVE
        )

        decision.final_category_id = (
            result.id
        )

        decision.approved_by = (
            request.user
            if request.user.is_authenticated
            else None
        )

        decision.approved_at = timezone.now()

        decision.review_comment = (
            request.data.get(
                "comment",
                ""
            )
        )

        decision.save()

        return Response(
            ResultSerializer(result).data
        )