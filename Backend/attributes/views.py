from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .models import ProductAttribute
from .serializers import ProductAttributeSerializer
from .services import AttributeExtractionService


class ProductAttributeView(APIView):

    def get(self, request, product_id):

        product = get_object_or_404(
            Product,
            id=product_id
        )

        attributes = ProductAttribute.objects.filter(
            product=product
        ).select_related(
            'attribute',
            'value'
        )

        serializer = ProductAttributeSerializer(
            attributes,
            many=True
        )

        return Response(serializer.data)

    def post(self, request, product_id):

        product = get_object_or_404(
            Product,
            id=product_id
        )

        service = AttributeExtractionService(
            product
        )

        attributes = service.extract()

        serializer = ProductAttributeSerializer(
            attributes,
            many=True
        )

        return Response(
            {
                'product_id': product.id,
                'count': len(attributes),
                'attributes': serializer.data,
            },
            status=status.HTTP_200_OK
        )