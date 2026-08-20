from django.test import TestCase

from .models import ProductAttribute


class ProductAttributeModelTest(TestCase):

    def test_product_attribute_table_exists(self):
        count = ProductAttribute.objects.count()

        self.assertEqual(count, 0)