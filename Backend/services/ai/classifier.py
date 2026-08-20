from typing import Iterable

from .schemas import (
    InferenceResult,
    ProductInput,
)
from .taxonomy_matcher import TaxonomyMatcher


class ProductClassifier:
    """
    Taxonomy-aware baseline classifier.

    The interface is intentionally independent of the
    underlying AI model so that an ML/LLM implementation
    can replace this later.
    """

    MODEL_NAME = "taxonomy-rule-classifier"
    MODEL_VERSION = "1.0"

    def __init__(
        self,
        categories: Iterable,
    ):

        self.matcher = TaxonomyMatcher(
            categories
        )

    def predict(
        self,
        product: ProductInput,
        limit: int = 5,
    ) -> InferenceResult:

        combined_text = (
            product.combined_text()
        )

        if not combined_text.strip():

            return InferenceResult(
                product_id=product.product_id,
                predicted_category_id=None,
                predicted_category_shopify_id=None,
                predicted_category_name=None,
                predicted_category_path=None,
                confidence=0.0,
                modality="text",
                success=False,
                error=(
                    "No textual product "
                    "information available."
                ),
                matched_text="",
                metadata={
                    "model": self.MODEL_NAME,
                    "version": self.MODEL_VERSION,
                },
            )

        candidates = self.matcher.match(
            product,
            limit=limit,
        )

        if not candidates:

            return InferenceResult(
                product_id=product.product_id,
                predicted_category_id=None,
                predicted_category_shopify_id=None,
                predicted_category_name=None,
                predicted_category_path=None,
                confidence=0.0,
                modality="text",
                success=False,
                error=(
                    "No matching taxonomy "
                    "category found."
                ),
                matched_text=combined_text,
                metadata={
                    "model": self.MODEL_NAME,
                    "version": self.MODEL_VERSION,
                },
            )

        primary = candidates[0]

        return InferenceResult(
            product_id=product.product_id,
            predicted_category_id=(
                primary.category_id
            ),
            predicted_category_shopify_id=(
                primary.shopify_id
            ),
            predicted_category_name=(
                primary.name
            ),
            predicted_category_path=(
                primary.full_name
            ),
            confidence=primary.score,
            alternatives=candidates[1:],
            modality=(
                "image+text"
                if product.image_url
                else "text"
            ),
            success=True,
            matched_text=combined_text,
            metadata={
                "model": self.MODEL_NAME,
                "version": self.MODEL_VERSION,
                "candidate_count": len(
                    candidates
                ),
            },
        )