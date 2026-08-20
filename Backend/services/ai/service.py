from typing import Iterable

from .attribute_extractor import (
    AttributeExtractor,
)
from .classifier import (
    ProductClassifier,
)
from .image_processor import (
    ImageProcessor,
)
from .schemas import (
    InferenceResult,
    ProductInput,
)


class AIInferenceService:
    """
    Main AI capability facade.

    Processing should communicate with this class
    instead of directly calling individual AI components.
    """

    def __init__(
        self,
        categories: Iterable,
    ):

        self.classifier = ProductClassifier(
            categories
        )

        self.attribute_extractor = (
            AttributeExtractor()
        )

        self.image_processor = (
            ImageProcessor()
        )

    def infer(
        self,
        product: ProductInput,
    ) -> InferenceResult:

        # -----------------------------------------
        # IMAGE
        # -----------------------------------------

        image_result = (
            self.image_processor.validate(
                product.image_url
            )
        )

        if image_result.valid:

            modality = "image+text"

        else:

            modality = "text"

        # -----------------------------------------
        # CLASSIFICATION
        # -----------------------------------------

        result = self.classifier.predict(
            product
        )

        result.modality = modality

        # -----------------------------------------
        # ATTRIBUTES
        # -----------------------------------------

        result.attributes = (
            self.attribute_extractor.extract(
                product
            )
        )

        # -----------------------------------------
        # IMAGE FALLBACK
        # -----------------------------------------

        if (
            product.image_url
            and not image_result.valid
        ):

            result.metadata[
                "image_fallback"
            ] = True

            result.metadata[
                "image_error"
            ] = image_result.error

        return result