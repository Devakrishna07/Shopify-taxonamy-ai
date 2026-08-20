import re
from decimal import Decimal

from django.db import transaction
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from products.models import Product
from taxonamy.models import TaxonomyCategory
from classification.models import (
    ClassificationResult,
    ClassificationCandidate,
)


class ClassificationService:

    HIGH_CONFIDENCE = 0.85
    REVIEW_CONFIDENCE = 0.65

    def normalize_text(self, text):
        """
        Normalize text for classification.
        """

        if not text:
            return ""

        text = str(text).lower()

        text = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def build_product_text(self, product):
        """
        Combine all useful product fields.
        """

        fields = [
            product.title,
            product.description,
            product.brand,
            product.product_type,
            product.existing_category,
            product.existing_subcategory,
        ]

        text = " ".join(
            str(value)
            for value in fields
            if value
        )

        return self.normalize_text(text)

    def build_category_text(self, category):
        """
        Build searchable category text.
        """

        values = [
            category.name,
            category.full_name,
        ]

        text = " ".join(
            str(value)
            for value in values
            if value
        )

        return self.normalize_text(text)

    def tokenize(self, text):
        return set(
            self.normalize_text(text).split()
        )

    def keyword_score(self, product_text, category_text):
        """
        Basic lexical overlap score.
        """

        product_tokens = self.tokenize(product_text)
        category_tokens = self.tokenize(category_text)

        if not product_tokens or not category_tokens:
            return 0.0

        intersection = product_tokens.intersection(
            category_tokens
        )

        return len(intersection) / len(category_tokens)

    def title_product_type_score(self, product):
        """
        Score based on title and product_type.
        """

        title = self.normalize_text(
            product.title
        )

        product_type = self.normalize_text(
            product.product_type
        )

        if not title and not product_type:
            return 0.0

        text = f"{title} {product_type}"

        return len(self.tokenize(text)) / max(
            len(self.tokenize(text)),
            1
        )

    def semantic_scores(
        self,
        product_text,
        category_texts
    ):
        """
        TF-IDF cosine similarity between
        product text and taxonomy categories.
        """

        if not product_text:
            return [0.0] * len(category_texts)

        documents = [
            product_text,
            *category_texts
        ]

        vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        try:
            matrix = vectorizer.fit_transform(
                documents
            )
        except ValueError:
            return [0.0] * len(category_texts)

        product_vector = matrix[0]
        category_vectors = matrix[1:]

        similarities = cosine_similarity(
            product_vector,
            category_vectors
        )[0]

        return similarities.tolist()

    def hierarchy_score(self, category):
        """
        Small structured consistency score.

        Leaf categories are preferred because Shopify
        classification should normally resolve to the
        most specific applicable category.
        """

        if getattr(category, "is_leaf", False):
            return 1.0

        return 0.5

    def confidence_level(self, confidence):
        if confidence >= self.HIGH_CONFIDENCE:
            return "HIGH"

        if confidence >= self.REVIEW_CONFIDENCE:
            return "REVIEW"

        return "MANUAL_REVIEW"

    def classify_product(self, product_id):
        """
        Main classification entry point.
        """

        product = Product.objects.get(
            id=product_id
        )

        product_text = self.build_product_text(
            product
        )

        if not product_text:
            raise ValueError(
                "Product does not contain enough text for classification."
            )

        categories = list(
            TaxonomyCategory.objects.all()
        )

        if not categories:
            raise ValueError(
                "No taxonomy categories are available."
            )

        category_texts = [
            self.build_category_text(category)
            for category in categories
        ]

        semantic_scores = self.semantic_scores(
            product_text,
            category_texts
        )

        candidates = []

        for index, category in enumerate(categories):

            semantic_score = float(
                semantic_scores[index]
            )

            keyword = self.keyword_score(
                product_text,
                category_texts[index]
            )

            hierarchy = self.hierarchy_score(
                category
            )

            # For this sprint attribute/image signals
            # are not yet implemented.
            attribute_score = 0.0

            # Combined text signal.
            combined_text = (
                (semantic_score * 0.70)
                + (keyword * 0.30)
            )

            # Current MVP score.
            #
            # Semantic text      40%
            # Title/product type 20%
            # Hierarchy           10%
            #
            # Remaining 30% is renormalized because
            # attribute/image modules are implemented
            # in later sprints.
            base_score = (
                (combined_text * 0.40)
                + (self.title_product_type_score(product) * 0.20)
                + (hierarchy * 0.10)
            )

            # Renormalize implemented weights.
            score = base_score / 0.70

            score = min(
                max(score, 0.0),
                1.0
            )

            candidates.append({
                "category": category,
                "score": score,
                "semantic_score": semantic_score,
                "keyword_score": keyword,
                "hierarchy_score": hierarchy,
            })

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        top_candidates = candidates[:5]

        if not top_candidates:
            raise ValueError(
                "Unable to generate classification candidates."
            )

        best = top_candidates[0]

        confidence = best["score"]

        if confidence >= self.HIGH_CONFIDENCE:
            status = "CLASSIFIED"

        elif confidence >= self.REVIEW_CONFIDENCE:
            status = "REVIEW"

        else:
            status = "REVIEW"

        reason = (
            f"Semantic score: "
            f"{best['semantic_score']:.3f}; "
            f"keyword score: "
            f"{best['keyword_score']:.3f}; "
            f"hierarchy score: "
            f"{best['hierarchy_score']:.3f}; "
            f"confidence level: "
            f"{self.confidence_level(confidence)}"
        )

        with transaction.atomic():

            result, _ = ClassificationResult.objects.update_or_create(
                product=product,
                defaults={
                    "category": best["category"],
                    "confidence": Decimal(
                        str(round(confidence, 5))
                    ),
                    "text_score": Decimal(
                        str(round(best["semantic_score"], 5))
                    ),
                    "attribute_score": Decimal("0"),
                    "image_score": None,
                    "status": status,
                    "reason": reason,
                },
            )

            ClassificationCandidate.objects.filter(
                product=product
            ).delete()

            for rank, candidate in enumerate(
                top_candidates,
                start=1
            ):

                ClassificationCandidate.objects.create(
                    product=product,
                    category=candidate["category"],
                    score=Decimal(
                        str(round(
                            candidate["score"],
                            5
                        ))
                    ),
                    rank=rank,
                    source="COMBINED",
                )

            product.normalized_text = product_text
            product.status = (
                "REVIEW"
                if status == "REVIEW"
                else "COMPLETED"
            )

            product.save(
                update_fields=[
                    "normalized_text",
                    "status",
                    "updated_at",
                ]
            )

        return result

    