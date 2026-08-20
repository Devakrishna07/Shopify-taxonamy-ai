from django.test import TestCase

from .service import AIInferenceService
from .schemas import ProductInput


class FakeCategory:
    """
    Test double matching the real TaxonomyCategory model.

    Real model fields:
        id
        shopify_id
        name
        full_name
        parent_id
        level
        is_root
        is_leaf
        is_archived
    """

    def __init__(
        self,
        category_id,
        shopify_id,
        name,
        full_name,
        parent_id=None,
        level=0,
        is_root=False,
        is_leaf=True,
        is_archived=False,
    ):
        self.id = category_id
        self.shopify_id = shopify_id
        self.name = name
        self.full_name = full_name
        self.parent_id = parent_id
        self.level = level
        self.is_root = is_root
        self.is_leaf = is_leaf
        self.is_archived = is_archived


class AIInferenceServiceTests(TestCase):

    def setUp(self):

        self.categories = [

            FakeCategory(
                category_id=1,
                shopify_id="gid://shopify/1",
                name="T-Shirts",
                full_name=(
                    "Apparel & Accessories > "
                    "Clothing > Shirts & Tops > "
                    "T-Shirts"
                ),
                level=4,
                is_leaf=True,
            ),

            FakeCategory(
                category_id=2,
                shopify_id="gid://shopify/2",
                name="Jeans",
                full_name=(
                    "Apparel & Accessories > "
                    "Clothing > Pants > Jeans"
                ),
                level=4,
                is_leaf=True,
            ),

            FakeCategory(
                category_id=3,
                shopify_id="gid://shopify/3",
                name="Sneakers",
                full_name=(
                    "Apparel & Accessories > "
                    "Shoes > Sneakers"
                ),
                level=3,
                is_leaf=True,
            ),

            FakeCategory(
                category_id=4,
                shopify_id="gid://shopify/4",
                name="Dresses",
                full_name=(
                    "Apparel & Accessories > "
                    "Clothing > Dresses"
                ),
                level=3,
                is_leaf=True,
            ),

        ]

        self.service = AIInferenceService(
            self.categories
        )

    # =====================================================
    # 1. TEXT CLASSIFICATION
    # =====================================================

    def test_text_product_classification(self):

        product = ProductInput(
            product_id=1,
            title="Men Black Cotton T-Shirt",
            description=(
                "Comfortable cotton t-shirt "
                "for everyday wear"
            ),
            product_type="T-Shirt",
            brand="Example Brand",
        )

        result = self.service.infer(product)

        self.assertTrue(result.success)

        self.assertEqual(
            result.predicted_category_id,
            1,
        )

        self.assertEqual(
            result.predicted_category_shopify_id,
            "gid://shopify/1",
        )

        self.assertEqual(
            result.predicted_category_name,
            "T-Shirts",
        )

        self.assertGreater(
            result.confidence,
            0,
        )

    # =====================================================
    # 2. ATTRIBUTE EXTRACTION
    # =====================================================

    def test_attribute_extraction(self):

        product = ProductInput(
            product_id=2,
            title="Black Cotton T-Shirt",
            description=(
                "Large men's cotton shirt"
            ),
        )

        result = self.service.infer(product)

        attributes = {
            (
                attribute.name,
                attribute.value,
            )
            for attribute in result.attributes
        }

        self.assertIn(
            ("color", "black"),
            attributes,
        )

        self.assertIn(
            ("material", "cotton"),
            attributes,
        )

        self.assertIn(
            ("size", "large"),
            attributes,
        )

    # =====================================================
    # 3. IMAGE + TEXT
    # =====================================================

    def test_image_plus_text_mode(self):

        product = ProductInput(
            product_id=3,
            title="Blue Sneakers",
            description=(
                "Sports running shoes"
            ),
            image_url=(
                "https://example.com/"
                "sneakers.jpg"
            ),
        )

        result = self.service.infer(product)

        self.assertTrue(
            result.success
        )

        self.assertEqual(
            result.modality,
            "image+text",
        )

        self.assertEqual(
            result.predicted_category_id,
            3,
        )

    # =====================================================
    # 4. NO IMAGE → TEXT FALLBACK
    # =====================================================

    def test_missing_image_uses_text_fallback(self):

        product = ProductInput(
            product_id=4,
            title="Red Cotton T-Shirt",
            description=(
                "Men's casual shirt"
            ),
            image_url=None,
        )

        result = self.service.infer(product)

        self.assertTrue(
            result.success
        )

        self.assertEqual(
            result.modality,
            "text",
        )

    # =====================================================
    # 5. INVALID IMAGE → TEXT FALLBACK
    # =====================================================

    def test_invalid_image_uses_text_fallback(self):

        product = ProductInput(
            product_id=5,
            title="Black T-Shirt",
            description="Cotton shirt",
            image_url="not-a-valid-image-url",
        )

        result = self.service.infer(product)

        self.assertTrue(
            result.success
        )

        self.assertEqual(
            result.modality,
            "text",
        )

        self.assertTrue(
            result.metadata.get(
                "image_fallback"
            )
        )

        self.assertIsNotNone(
            result.metadata.get(
                "image_error"
            )
        )

    # =====================================================
    # 6. MISSING DESCRIPTION
    # =====================================================

    def test_missing_description_does_not_fail(self):

        product = ProductInput(
            product_id=6,
            title="Black Cotton T-Shirt",
            description="",
        )

        result = self.service.infer(product)

        self.assertTrue(
            result.success
        )

        self.assertEqual(
            result.predicted_category_id,
            1,
        )

    # =====================================================
    # 7. MISSING ALL TEXT
    # =====================================================

    def test_missing_all_text_fails_gracefully(self):

        product = ProductInput(
            product_id=7,
            title="",
            description="",
            product_type="",
            brand="",
        )

        result = self.service.infer(product)

        self.assertFalse(
            result.success
        )

        self.assertEqual(
            result.confidence,
            0.0,
        )

        self.assertIsNotNone(
            result.error
        )

        self.assertIsNone(
            result.predicted_category_id
        )

    # =====================================================
    # 8. UNKNOWN PRODUCT
    # =====================================================

    def test_unknown_product_fails_gracefully(self):

        product = ProductInput(
            product_id=8,
            title="Electric Garden Motor",
            description=(
                "A completely unrelated "
                "mechanical product"
            ),
        )

        result = self.service.infer(product)

        self.assertFalse(
            result.success
        )

        self.assertIsNone(
            result.predicted_category_id
        )

        self.assertEqual(
            result.confidence,
            0.0,
        )

        self.assertIn(
            "No matching taxonomy",
            result.error,
        )

    # =====================================================
    # 9. ALTERNATIVE CATEGORIES
    # =====================================================

    def test_alternative_categories_are_returned(self):

        product = ProductInput(
            product_id=9,
            title="Clothing Shirt",
            description=(
                "Apparel clothing product"
            ),
        )

        result = self.service.infer(
            product
        )

        self.assertLessEqual(
            len(result.alternatives),
            4,
        )

        for alternative in (
            result.alternatives
        ):
            self.assertIsNotNone(
                alternative.category_id
            )

            self.assertIsNotNone(
                alternative.shopify_id
            )

            self.assertIsNotNone(
                alternative.name
            )

            self.assertIsNotNone(
                alternative.full_name
            )

            self.assertGreaterEqual(
                alternative.score,
                0.0,
            )

    # =====================================================
    # 10. METADATA
    # =====================================================

    def test_result_contains_metadata(self):

        product = ProductInput(
            product_id=10,
            title="Cotton T-Shirt",
        )

        result = self.service.infer(
            product
        )

        self.assertIn(
            "model",
            result.metadata,
        )

        self.assertIn(
            "version",
            result.metadata,
        )

        self.assertIn(
            "candidate_count",
            result.metadata,
        )

    # =====================================================
    # 11. SHOPIFY TAXONOMY ID
    # =====================================================

    def test_shopify_taxonomy_id_is_returned(self):

        product = ProductInput(
            product_id=11,
            title="Black Cotton T-Shirt",
        )

        result = self.service.infer(
            product
        )

        self.assertEqual(
            result.predicted_category_shopify_id,
            "gid://shopify/1",
        )

    # =====================================================
    # 12. FULL TAXONOMY PATH
    # =====================================================

    def test_full_taxonomy_path_is_returned(self):

        product = ProductInput(
            product_id=12,
            title="Black Cotton T-Shirt",
        )

        result = self.service.infer(
            product
        )

        self.assertEqual(
            result.predicted_category_path,
            (
                "Apparel & Accessories > "
                "Clothing > Shirts & Tops > "
                "T-Shirts"
            ),
        )

    # =====================================================
    # 13. ARCHIVED CATEGORY IS IGNORED
    # =====================================================

    def test_archived_category_is_ignored(self):

        archived_category = FakeCategory(
            category_id=99,
            shopify_id="gid://shopify/99",
            name="T-Shirts",
            full_name=(
                "Archived > T-Shirts"
            ),
            is_leaf=True,
            is_archived=True,
        )

        service = AIInferenceService(
            self.categories
            + [archived_category]
        )

        product = ProductInput(
            product_id=13,
            title="Black Cotton T-Shirt",
        )

        result = service.infer(
            product
        )

        self.assertTrue(
            result.success
        )

        self.assertNotEqual(
            result.predicted_category_id,
            99,
        )

    # =====================================================
    # 14. IMAGE FAILURE DOES NOT FAIL PRODUCT
    # =====================================================

    def test_image_failure_does_not_fail_product(self):

        product = ProductInput(
            product_id=14,
            title="Black Cotton T-Shirt",
            image_url="invalid-image",
        )

        result = self.service.infer(
            product
        )

        self.assertTrue(
            result.success
        )

        self.assertEqual(
            result.modality,
            "text",
        )

        self.assertTrue(
            result.metadata.get(
                "image_fallback"
            )
        )

    # =====================================================
    # 15. PRODUCT ID IS PRESERVED
    # =====================================================

    def test_product_id_is_preserved(self):

        product = ProductInput(
            product_id=12345,
            title="Black T-Shirt",
        )

        result = self.service.infer(
            product
        )

        self.assertEqual(
            result.product_id,
            12345,
        )