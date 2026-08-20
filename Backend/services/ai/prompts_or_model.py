from typing import Dict

from .schemas import ProductInput


class ModelAdapter:
    """
    Stable interface for a future ML/LLM implementation.

    Do not put provider-specific code inside Processing.
    """

    MODEL_NAME = "baseline"

    def build_input(
        self,
        product: ProductInput,
    ) -> Dict:

        return {
            "product_id": product.product_id,
            "title": product.title,
            "description": product.description,
            "product_type": product.product_type,
            "brand": product.brand,
            "image_url": product.image_url,
            "reviews": product.reviews,
            "extra_signals": product.extra_signals,
        }

    def predict(self, product: ProductInput):
        """
        Placeholder interface for a future actual ML/LLM model.

        The baseline system currently uses ProductClassifier.
        """

        raise NotImplementedError(
            "Connect an ML/LLM model implementation here."
        )