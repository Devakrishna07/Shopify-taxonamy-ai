from django.utils import timezone

from products.models import Product
from processing.models import ProcessingJob


class ProductPipeline:

    """
    Orchestrates the already implemented modules.

    Processing should NOT contain the classification,
    attribute extraction, or review business logic itself.
    """

    def __init__(self, product):
        self.product = product

    def run(self):
        """
        Execute the complete product pipeline.
        """

        self._set_status("PROCESSING")

        try:
            # -------------------------------------------------
            # STEP 1: CLASSIFICATION
            # -------------------------------------------------
            classification_result = self.run_classification()

            # -------------------------------------------------
            # STEP 2: ATTRIBUTES
            # -------------------------------------------------
            attribute_result = self.run_attributes(
                classification_result
            )

            # -------------------------------------------------
            # STEP 3: DETERMINE FINAL STATUS
            # -------------------------------------------------
            self.update_final_status(
                classification_result
            )

            return {
                "success": True,
                "product_id": self.product.id,
                "classification": classification_result,
                "attributes": attribute_result,
                "status": self.product.status,
            }

        except Exception as exc:

            self._set_status("FAILED")

            return {
                "success": False,
                "product_id": self.product.id,
                "error": str(exc),
                "status": "FAILED",
            }

    def run_classification(self):
        """
        Connect this method to your existing classification module.
        """

        from services.classification_service import classify_product

        return classify_product(self.product)

    def run_attributes(self, classification_result):
        """
        Connect this method to your existing attributes module.
        """

        from attributes.services import extract_product_attributes

        return extract_product_attributes(
            self.product,
            classification_result
        )

    def update_final_status(self, classification_result):

        confidence = None

        if isinstance(classification_result, dict):
            confidence = classification_result.get(
                "confidence"
            )

        if confidence is not None and confidence < 0.65:

            self._set_status("REVIEW")

        else:

            self._set_status("COMPLETED")

    def _set_status(self, status):

        self.product.status = status

        self.product.updated_at = timezone.now()

        self.product.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )