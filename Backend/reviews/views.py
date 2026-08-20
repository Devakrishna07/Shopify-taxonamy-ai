from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ReviewAction
from .serializers import ReviewActionSerializer

from products.models import Product


class ReviewListView(APIView):

    def get(self, request):
        reviews = ReviewAction.objects.all().order_by("-created_at")

        serializer = ReviewActionSerializer(
            reviews,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = ReviewActionSerializer(
            data=request.data
        )

        if serializer.is_valid():
            review = serializer.save()

            return Response(
                ReviewActionSerializer(review).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ReviewDetailView(APIView):

    def get(self, request, pk):

        try:
            review = ReviewAction.objects.get(pk=pk)

        except ReviewAction.DoesNotExist:
            return Response(
                {"detail": "Review not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ReviewActionSerializer(review)

        return Response(serializer.data)


class ApproveReviewView(APIView):

    def post(self, request, pk):

        try:
            product = Product.objects.get(pk=pk)

        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        old_category_id = request.data.get(
            "old_category_id"
        )

        comment = request.data.get(
            "comment",
            ""
        )

        review = ReviewAction.objects.create(
            product=product,
            old_category_id=old_category_id,
            new_category_id=old_category_id,
            action=ReviewAction.APPROVE,
            comment=comment,
        )

        return Response(
            ReviewActionSerializer(review).data,
            status=status.HTTP_201_CREATED
        )


class EditReviewView(APIView):

    def post(self, request, pk):

        try:
            product = Product.objects.get(pk=pk)

        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        old_category_id = request.data.get(
            "old_category_id"
        )

        new_category_id = request.data.get(
            "new_category_id"
        )

        if not new_category_id:
            return Response(
                {
                    "detail": "new_category_id is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        comment = request.data.get(
            "comment",
            ""
        )

        review = ReviewAction.objects.create(
            product=product,
            old_category_id=old_category_id,
            new_category_id=new_category_id,
            action=ReviewAction.EDIT,
            comment=comment,
        )

        return Response(
            ReviewActionSerializer(review).data,
            status=status.HTTP_201_CREATED
        )


class RejectReviewView(APIView):

    def post(self, request, pk):

        try:
            product = Product.objects.get(pk=pk)

        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        old_category_id = request.data.get(
            "old_category_id"
        )

        comment = request.data.get(
            "comment",
            ""
        )

        review = ReviewAction.objects.create(
            product=product,
            old_category_id=old_category_id,
            new_category_id=None,
            action=ReviewAction.REJECT,
            comment=comment,
        )

        return Response(
            ReviewActionSerializer(review).data,
            status=status.HTTP_201_CREATED
        )