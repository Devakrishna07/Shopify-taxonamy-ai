import re

from typing import List

from .schemas import (
    AttributeValue,
    ProductInput,
)


class AttributeExtractor:
    """
    Baseline attribute extractor.

    This extracts obvious product attributes from
    the available textual signals.

    The existing Attributes Django module remains
    responsible for persistence/business logic.
    """

    COLOR_WORDS = {
        "black",
        "white",
        "red",
        "blue",
        "green",
        "yellow",
        "orange",
        "pink",
        "purple",
        "brown",
        "grey",
        "gray",
        "beige",
        "navy",
    }

    SIZE_WORDS = {
        "xs",
        "s",
        "m",
        "l",
        "xl",
        "xxl",
        "small",
        "medium",
        "large",
    }

    MATERIAL_WORDS = {
        "cotton",
        "leather",
        "silk",
        "wool",
        "linen",
        "polyester",
        "nylon",
        "denim",
        "plastic",
        "steel",
        "wood",
    }

    def _contains_word(
        self,
        text: str,
        word: str,
    ) -> bool:

        return (
            re.search(
                rf"\b{re.escape(word)}\b",
                text,
                flags=re.IGNORECASE,
            )
            is not None
        )

    def extract(
        self,
        product: ProductInput,
    ) -> List[AttributeValue]:

        text = product.combined_text()

        if not text.strip():
            return []

        attributes = []

        for color in self.COLOR_WORDS:

            if self._contains_word(
                text,
                color,
            ):
                attributes.append(
                    AttributeValue(
                        name="color",
                        value=color,
                        confidence=0.90,
                    )
                )

        for size in self.SIZE_WORDS:

            if self._contains_word(
                text,
                size,
            ):
                attributes.append(
                    AttributeValue(
                        name="size",
                        value=size,
                        confidence=0.90,
                    )
                )

        for material in self.MATERIAL_WORDS:

            if self._contains_word(
                text,
                material,
            ):
                attributes.append(
                    AttributeValue(
                        name="material",
                        value=material,
                        confidence=0.90,
                    )
                )

        return attributes