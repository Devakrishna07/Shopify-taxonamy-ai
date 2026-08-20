import re
from typing import Iterable, List

from .schemas import (
    ProductInput,
    TaxonomyCandidate,
)


class TaxonomyMatcher:
    """
    Matches normalized product information against the
    existing taxonamy.TaxonomyCategory model.

    No new taxonomy database is created here.
    """

    STOP_WORDS = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "for",
        "with",
        "of",
        "to",
        "in",
        "on",
        "is",
        "new",
        "this",
        "that",
        "product",
    }

    def __init__(
        self,
        categories: Iterable,
    ):
        self.categories = list(categories)

    def _tokenize(self, text: str) -> set:

        text = (text or "").lower()

        words = re.findall(
            r"[a-z0-9]+",
            text,
        )

        return {
            word
            for word in words
            if word not in self.STOP_WORDS
        }

    def _category_values(self, category):

        return {
            "id": category.id,
            "shopify_id": category.shopify_id,
            "name": category.name or "",
            "full_name": category.full_name or "",
        }

    def match(
        self,
        product: ProductInput,
        limit: int = 5,
    ) -> List[TaxonomyCandidate]:

        product_text = product.combined_text()

        if not product_text.strip():
            return []

        product_tokens = self._tokenize(
            product_text
        )

        candidates = []

        for category in self.categories:

            if getattr(
                category,
                "is_archived",
                False,
            ):
                continue

            values = self._category_values(
                category
            )

            taxonomy_text = (
                f"{values['name']} "
                f"{values['full_name']}"
            )

            taxonomy_tokens = self._tokenize(
                taxonomy_text
            )

            if not taxonomy_tokens:
                continue

            matched_tokens = (
                product_tokens.intersection(
                    taxonomy_tokens
                )
            )

            if not matched_tokens:
                continue

            score = (
                len(matched_tokens)
                / max(
                    len(taxonomy_tokens),
                    1,
                )
            )

            # Stronger score when the actual category
            # name occurs in the product signals.
            name_tokens = self._tokenize(
                values["name"]
            )

            if (
                name_tokens
                and name_tokens.issubset(
                    product_tokens
                )
            ):
                score += 0.25

            # Slight boost for leaf categories because
            # Shopify classification normally targets
            # the most specific category.
            if getattr(
                category,
                "is_leaf",
                False,
            ):
                score += 0.05

            score = min(
                round(score, 4),
                1.0,
            )

            candidates.append(
                TaxonomyCandidate(
                    category_id=values["id"],
                    shopify_id=values["shopify_id"],
                    name=values["name"],
                    full_name=values["full_name"],
                    score=score,
                )
            )

        candidates.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return candidates[:limit]