import re
from decimal import Decimal

from .models import ProductAttribute


class AttributeExtractionService:

    def __init__(self, product):
        self.product = product

    def build_product_text(self):
        """
        Combine all available product information.
        Missing fields are ignored.
        """

        fields = [
            getattr(self.product, 'title', None),
            getattr(self.product, 'description', None),
            getattr(self.product, 'product_type', None),
            getattr(self.product, 'brand', None),
            getattr(self.product, 'existing_category', None),
            getattr(self.product, 'existing_subcategory', None),
        ]

        values = [
            str(value).strip()
            for value in fields
            if value
        ]

        return ' '.join(values)

    @staticmethod
    def normalize_text(text):
        text = text.lower()

        text = re.sub(
            r'[^a-z0-9\s\-]',
            ' ',
            text
        )

        text = re.sub(
            r'\s+',
            ' ',
            text
        )

        return text.strip()

    @staticmethod
    def calculate_confidence(
        product_text,
        taxonomy_value
    ):
        """
        Simple prototype confidence calculation.

        Exact value match gets highest confidence.
        Word occurrence gets lower confidence.
        """

        text = AttributeExtractionService.normalize_text(
            product_text
        )

        value = AttributeExtractionService.normalize_text(
            taxonomy_value
        )

        if not text or not value:
            return Decimal('0.00000')

        if value in text:
            return Decimal('0.95000')

        value_words = set(value.split())
        text_words = set(text.split())

        if not value_words:
            return Decimal('0.00000')

        overlap = len(value_words & text_words)

        score = overlap / len(value_words)

        if score >= 1:
            return Decimal('0.95000')

        if score >= 0.5:
            return Decimal('0.75000')

        if score > 0:
            return Decimal('0.55000')

        return Decimal('0.00000')

    def get_classification_category(self):
        """
        Get the category selected by the classification module.
        """

        try:
            result = self.product.classification_result
        except Exception:
            return None

        return getattr(result, 'category', None)

    def get_category_attributes(self, category):
        """
        Retrieve attributes applicable to the selected
        Shopify taxonomy category.
        """

        if not category:
            return []

        from taxonamy.models import CategoryAttribute

        relations = CategoryAttribute.objects.filter(
            category=category
        ).select_related('attribute')

        return [
            relation.attribute
            for relation in relations
        ]

    def find_matching_value(
        self,
        attribute,
        product_text
    ):
        """
        Search Shopify taxonomy values for this attribute.
        """

        from taxonamy.models import TaxonomyValue

        values = TaxonomyValue.objects.filter(
            attribute=attribute
        )

        best_value = None
        best_confidence = Decimal('0.00000')

        for value in values:

            confidence = self.calculate_confidence(
                product_text,
                value.value
            )

            if confidence > best_confidence:
                best_confidence = confidence
                best_value = value

        return best_value, best_confidence

    def extract(self):
        """
        Extract and persist product attributes.
        """

        category = self.get_classification_category()

        if not category:
            return []

        product_text = self.build_product_text()

        if not product_text:
            return []

        attributes = self.get_category_attributes(
            category
        )

        results = []

        for attribute in attributes:

            value, confidence = self.find_matching_value(
                attribute,
                product_text
            )

            if not value:
                continue

            if confidence <= Decimal('0.00000'):
                continue

            product_attribute, _ = (
                ProductAttribute.objects.update_or_create(
                    product=self.product,
                    attribute=attribute,
                    defaults={
                        'value': value,
                        'raw_value': value.value,
                        'confidence': confidence,
                    }
                )
            )

            results.append(product_attribute)

        return results