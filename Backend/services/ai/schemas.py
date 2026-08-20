from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProductInput:
    """
    Standard product representation passed from Processing
    to the AI inference layer.
    """

    product_id: Optional[Any] = None

    title: str = ""
    description: str = ""
    product_type: str = ""
    brand: str = ""

    image_url: Optional[str] = None

    reviews: List[str] = field(default_factory=list)

    extra_signals: Dict[str, Any] = field(
        default_factory=dict
    )

    def combined_text(self) -> str:
        """
        Combine every available textual signal.
        """

        parts = [
            self.title,
            self.description,
            self.product_type,
            self.brand,
        ]

        parts.extend(self.reviews)

        return " ".join(
            part.strip()
            for part in parts
            if isinstance(part, str)
            and part.strip()
        )


@dataclass
class TaxonomyCandidate:
    category_id: Any
    shopify_id: str
    name: str
    full_name: str
    score: float = 0.0


@dataclass
class AttributeValue:
    name: str
    value: str
    confidence: float = 0.0


@dataclass
class InferenceResult:
    """
    Standard result returned by the AI layer.
    """

    product_id: Optional[Any]

    predicted_category_id: Optional[Any]
    predicted_category_shopify_id: Optional[str]

    predicted_category_name: Optional[str]
    predicted_category_path: Optional[str]

    confidence: float

    alternatives: List[
        TaxonomyCandidate
    ] = field(default_factory=list)

    attributes: List[
        AttributeValue
    ] = field(default_factory=list)

    modality: str = "text"

    success: bool = True

    error: Optional[str] = None

    matched_text: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self):
        """
        Convert the result to a JSON/API-friendly dictionary.
        """

        return {
            "product_id": self.product_id,
            "predicted_category_id": (
                self.predicted_category_id
            ),
            "predicted_category_shopify_id": (
                self.predicted_category_shopify_id
            ),
            "predicted_category_name": (
                self.predicted_category_name
            ),
            "predicted_category_path": (
                self.predicted_category_path
            ),
            "confidence": self.confidence,
            "alternatives": [
                {
                    "category_id": candidate.category_id,
                    "shopify_id": candidate.shopify_id,
                    "name": candidate.name,
                    "full_name": candidate.full_name,
                    "score": candidate.score,
                }
                for candidate in self.alternatives
            ],
            "attributes": [
                {
                    "name": attribute.name,
                    "value": attribute.value,
                    "confidence": attribute.confidence,
                }
                for attribute in self.attributes
            ],
            "modality": self.modality,
            "success": self.success,
            "error": self.error,
            "matched_text": self.matched_text,
            "metadata": self.metadata,
        }