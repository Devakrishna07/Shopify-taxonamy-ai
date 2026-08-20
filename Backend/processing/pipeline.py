from django.utils import timezone

from products.models import Product
from processing.models import ProcessingJob

from taxonamy.models import TaxonomyCategory

from services.ai import (
    AIInferenceService,
    ProductInput,
)


class ProductPipeline:
    """
    Main orchestration layer for product processing.

    Responsibilities:
        1. Normalize product signals.
        2. Load Shopify taxonomy.
        3. Call AI inference.
        4. Pass classification to the existing
           Classification module.
        5. Pass AI attributes to the existing
           Attributes module.
        6. Persist taxonomy result.
        7. Determine processing status.
    """

    def __init__(self, product):

        self.product = product

        self.ai_service = None

    # =====================================================
    # MAIN PIPELINE
    # =====================================================

    def run(self):

        self._set_status(
            "PROCESSING"
        )

        try:

            # ---------------------------------------------
            # STEP 1
            # Normalize product
            # ---------------------------------------------

            product_input = (
                self.build_product_input()
            )

            # ---------------------------------------------
            # STEP 2
            # Load taxonomy
            # ---------------------------------------------

            categories = (
                TaxonomyCategory.objects.filter(
                    is_archived=False
                )
            )

            self.ai_service = (
                AIInferenceService(
                    categories
                )
            )

            # ---------------------------------------------
            # STEP 3
            # AI inference
            # ---------------------------------------------

            ai_result = (
                self.ai_service.infer(
                    product_input
                )
            )

            classification_result = (
                self.run_classification(
                    ai_result
                )
            )

            # ---------------------------------------------
            # STEP 4
            # Attributes
            # ---------------------------------------------

            attribute_result = (
                self.run_attributes(
                    classification_result,
                    ai_result,
                )
            )

            # ---------------------------------------------
            # STEP 5
            # Persist taxonomy result
            # ---------------------------------------------

            self.persist_taxonomy_result(
                ai_result
            )

            # ---------------------------------------------
            # STEP 6
            # Final status
            # ---------------------------------------------

            self.update_final_status(
                ai_result
            )

            return {

                "success": True,

                "product_id": (
                    self.product.id
                ),

                "classification": (
                    classification_result
                ),

                "ai_inference": (
                    ai_result.to_dict()
                ),

                "attributes": (
                    attribute_result
                ),

                "status": (
                    self.product.status
                ),
            }

        except Exception as exc:

            self._set_status(
                "FAILED"
            )

            return {

                "success": False,

                "product_id": (
                    self.product.id
                ),

                "error": str(exc),

                "status": "FAILED",
            }

    # =====================================================
    # PRODUCT INPUT
    # =====================================================

    def build_product_input(self):
        """
        Convert the existing Product model into
        the standard AI ProductInput schema.

        getattr() is intentionally used so this layer
        remains tolerant of optional product fields.
        """

        return ProductInput(

            product_id=(
                self.product.id
            ),

            title=(
                getattr(
                    self.product,
                    "title",
                    "",
                )
                or ""
            ),

            description=(
                getattr(
                    self.product,
                    "description",
                    "",
                )
                or ""
            ),

            product_type=(
                getattr(
                    self.product,
                    "product_type",
                    "",
                )
                or ""
            ),

            brand=(
                getattr(
                    self.product,
                    "brand",
                    "",
                )
                or ""
            ),

            image_url=self._get_image_url(),
        )

    # =====================================================
    # IMAGE
    # =====================================================

    def _get_image_url(self):

        image = getattr(
            self.product,
            "image",
            None,
        )

        if image:

            # Django ImageField
            try:

                return image.url

            except Exception:

                pass

        image_url = getattr(
            self.product,
            "image_url",
            None,
        )

        if image_url:

            return image_url

        return None

    # =====================================================
    # CLASSIFICATION
    # =====================================================

    def run_classification(
        self,
        ai_result,
    ):
        """
        Existing Classification module remains in
        the architecture.

        AI inference supplies the predicted category,
        confidence and alternatives.

        If your existing classification service supports
        an AI result argument, it will be used.

        Otherwise the AI result itself becomes the
        classification output.
        """

        try:

            from services.classification_service import (
                classify_product,
            )

            try:

                return classify_product(
                    self.product,
                    ai_result.to_dict(),
                )

            except TypeError:

                return classify_product(
                    self.product
                )

        except ImportError:

            return ai_result.to_dict()

    # =====================================================
    # ATTRIBUTES
    # =====================================================

    def run_attributes(
        self,
        classification_result,
        ai_result,
    ):
        """
        Existing Attributes module remains responsible
        for attribute persistence/business logic.

        AI extracted attributes are supplied as additional
        evidence.
        """

        try:

            from attributes.services import (
                extract_product_attributes,
            )

            try:

                return extract_product_attributes(
                    self.product,
                    classification_result,
                    ai_result.to_dict(),
                )

            except TypeError:

                return extract_product_attributes(
                    self.product,
                    classification_result,
                )

        except ImportError:

            return [
                {
                    "name": attribute.name,
                    "value": attribute.value,
                    "confidence": (
                        attribute.confidence
                    ),
                }
                for attribute
                in ai_result.attributes
            ]

    # =====================================================
    # PERSIST TAXONOMY RESULT
    # =====================================================

    def persist_taxonomy_result(
        self,
        ai_result,
    ):

        from taxonamy.models import (
            ProductTaxonomyResult,
        )

        category = None

        if (
            ai_result.predicted_category_id
        ):

            category = (
                TaxonomyCategory.objects.filter(
                    id=(
                        ai_result
                        .predicted_category_id
                    ),
                    is_archived=False,
                ).first()
            )

        ProductTaxonomyResult.objects.update_or_create(

            product=self.product,

            defaults={

                "category": category,

                "confidence": (
                    ai_result.confidence
                ),

                "matched_text": (
                    ai_result.matched_text
                ),

                "status": (
                    self._taxonomy_result_status(
                        ai_result
                    )
                ),
            },
        )

    # =====================================================
    # TAXONOMY RESULT STATUS
    # =====================================================

    def _taxonomy_result_status(
        self,
        ai_result,
    ):

        if not ai_result.success:

            return "failed"

        if ai_result.confidence >= 0.85:

            return "auto_approved"

        if ai_result.confidence >= 0.60:

            return "needs_review"

        return "manual_review"

    # =====================================================
    # FINAL PROCESSING STATUS
    # =====================================================

    def update_final_status(
        self,
        ai_result,
    ):

        if not ai_result.success:

            self._set_status(
                "FAILED"
            )

            return

        confidence = (
            ai_result.confidence
        )

        if confidence >= 0.85:

            self._set_status(
                "COMPLETED"
            )

        elif confidence >= 0.60:

            self._set_status(
                "REVIEW"
            )

        else:

            self._set_status(
                "REVIEW"
            )

    # =====================================================
    # PRODUCT STATUS
    # =====================================================

    def _set_status(
        self,
        status,
    ):

        self.product.status = status

        self.product.updated_at = (
            timezone.now()
        )

        self.product.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )