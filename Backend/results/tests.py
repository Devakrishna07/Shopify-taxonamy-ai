from django.urls import reverse

from rest_framework.test import APITestCase

from products.models import Product
from classification.models import ClassificationResult


class ResultsAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):

        cls.product = Product.objects.create(
            title="Test Cotton Shirt",
            sku="TEST-001",
            product_type="Shirt",
            status="CLASSIFIED",
        )

        cls.result = ClassificationResult.objects.create(
            product=cls.product,
            confidence=0.91,
            status="HIGH",
        )

    def test_results_list(self):

        response = self.client.get(
            "/api/results/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_result_detail(self):

        response = self.client.get(
            f"/api/results/{self.result.id}/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_product_result(self):

        response = self.client.get(
            f"/api/results/product/{self.product.id}/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_summary(self):

        response = self.client.get(
            "/api/results/summary/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_search(self):

        response = self.client.get(
            "/api/results/?search=shirt"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_confidence_filter(self):

        response = self.client.get(
            "/api/results/?min_confidence=0.85"
        )

        self.assertEqual(
            response.status_code,
            200
        )