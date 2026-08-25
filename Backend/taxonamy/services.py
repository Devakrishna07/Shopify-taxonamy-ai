
import re
from collections import defaultdict

from django.db.models import Prefetch

from .models import (
    TaxonomyCategory,
    TaxonomyValue,
    ProductTaxonomyResult,
    CategoryAttribute,
)

from .ai_classifier import (
    TaxonomyAIClassifier,
    TaxonomyAIError,
)


HIGH_CONFIDENCE = 0.85
REVIEW_CONFIDENCE = 0.60

MAX_ALTERNATIVES = 5
MAX_AI_CANDIDATES = 60


def normalize(value):
    if not value:
        return ""

    value = str(value).lower()

    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value,
    )

    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def tokens(value):
    return {
        word
        for word in normalize(value).split()
        if len(word) >= 3
    }


def safe_value(value):
    if value is None:
        return ""

    return str(value).strip()


def get_product_image_url(product):
    """
    Attempts to retrieve an image URL without assuming
    one specific Product/Image implementation.
    """

    try:
        images = getattr(
            product,
            "images",
            None,
        )

        if images is not None:
            image = images.first()

            if image:
                url = (
                    getattr(
                        image,
                        "image_url",
                        None,
                    )
                    or getattr(
                        image,
                        "url",
                        None,
                    )
                    or getattr(
                        image,
                        "src",
                        None,
                    )
                )

                if url:
                    return str(url)

    except Exception:
        pass

    try:
        image = getattr(
            product,
            "image",
            None,
        )

        if image:
            url = getattr(
                image,
                "url",
                None,
            )

            if url:
                return str(url)

    except Exception:
        pass

    try:
        image_url = getattr(
            product,
            "image_url",
            None,
        )

        if image_url:
            return str(image_url)

    except Exception:
        pass

    return None


def get_product_image_status(product):
    url = get_product_image_url(product)

    if not url:
        return "not_available"

    if not (
        url.startswith("http://")
        or url.startswith("https://")
    ):
        return "invalid"

    return "available"


def build_product_text(product):
    """
    Build a rich product representation.

    Fields are read defensively because imported Excel files
    may have missing columns.
    """

    fields = [
        ("title", "Product Title"),
        ("description", "Description"),
        ("product_type", "Product Type"),
        ("brand", "Brand"),
        ("existing_category", "Existing Category"),
        ("existing_subcategory", "Existing Subcategory"),
        ("tags", "Tags"),
        ("vendor", "Vendor"),
        ("normalized_text", "Normalized Text"),
    ]

    parts = []

    for field, label in fields:
        value = safe_value(
            getattr(product, field, "")
        )

        if not value:
            continue

        parts.append(
            f"{label}: {value}"
        )

    return "\n".join(parts)


def build_category_index():
    """
    Load the active Shopify taxonomy once per classification batch.
    """

    categories = list(
        TaxonomyCategory.objects
        .filter(
            is_archived=False,
        )
        .prefetch_related(
            Prefetch(
                "category_attributes",
                queryset=(
                    CategoryAttribute.objects
                    .select_related("attribute")
                    .order_by(
                        "-required",
                        "attribute__name",
                    )
                ),
            )
        )
    )

    index = defaultdict(set)

    for category in categories:
        category_text = normalize(
            f"{category.name} "
            f"{category.full_name}"
        )

        for token in tokens(category_text):
            index[token].add(
                category.id
            )

    category_map = {
        category.id: category
        for category in categories
    }

    return category_map, index


def generate_candidates(
    product_text,
    category_map,
    category_index,
):
    """
    Use token overlap only for candidate retrieval.

    The final decision is made by the AI model.
    """

    product_tokens = tokens(
        product_text
    )

    candidate_ids = set()

    for token in product_tokens:
        candidate_ids.update(
            category_index.get(
                token,
                set(),
            )
        )

    if not candidate_ids:
        return list(
            category_map.values()
        )[:MAX_AI_CANDIDATES]

    candidates = [
        category_map[category_id]
        for category_id in candidate_ids
        if category_id in category_map
    ]

    candidates.sort(
        key=lambda category: (
            category.is_leaf,
            category.level,
            len(
                tokens(
                    category.full_name
                )
                & product_tokens
            ),
        ),
        reverse=True,
    )

    return candidates[:MAX_AI_CANDIDATES]


def heuristic_score(
    product,
    category,
    product_text,
):
    """
    Used only to rank candidate alternatives.
    It is NOT the final AI classification score.
    """

    product_tokens = tokens(
        product_text
    )

    category_name_tokens = tokens(
        category.name
    )

    category_path_tokens = tokens(
        category.full_name
    )

    if not product_tokens:
        return 0.0, []

    matched = set()

    name_matches = (
        product_tokens
        & category_name_tokens
    )

    path_matches = (
        product_tokens
        & category_path_tokens
    )

    matched.update(name_matches)
    matched.update(path_matches)

    score = 0.0

    if name_matches:
        score += min(
            0.50,
            len(name_matches) * 0.15,
        )

    if path_matches:
        score += min(
            0.30,
            len(path_matches) * 0.08,
        )

    product_type = normalize(
        getattr(
            product,
            "product_type",
            "",
        )
    )

    if product_type:
        type_matches = (
            tokens(product_type)
            & category_path_tokens
        )

        if type_matches:
            score += min(
                0.15,
                len(type_matches) * 0.08,
            )

            matched.update(
                type_matches
            )

    if category.is_leaf:
        score += 0.05

    return (
        min(score, 1.0),
        sorted(matched),
    )


def extract_attributes(
    product,
    category,
    product_text,
):
    """
    Detect category-specific Shopify attributes and
    matching values from the product information.
    """

    if not category:
        return []

    results = []

    try:
        category_attributes = (
            CategoryAttribute.objects
            .filter(
                category=category,
            )
            .select_related(
                "attribute",
            )
            .prefetch_related(
                "attribute__values",
            )
            .order_by(
                "-required",
                "attribute__name",
            )
        )

    except Exception:
        return results

    product_tokens = tokens(
        product_text
    )

    for relation in category_attributes:
        attribute = relation.attribute

        values = []

        try:
            taxonomy_values = (
                attribute.values.all()
            )
        except Exception:
            taxonomy_values = []

        for value in taxonomy_values:
            value_tokens = tokens(
                value.name
            )

            matches = (
                value_tokens
                & product_tokens
            )

            if not matches:
                continue

            confidence = min(
                1.0,
                0.70
                + (
                    len(matches)
                    * 0.10
                ),
            )

            values.append(
                {
                    "id": value.id,
                    "shopify_id": value.shopify_id,
                    "name": value.name,
                    "confidence": round(
                        confidence,
                        4,
                    ),
                }
            )

        results.append(
            {
                "attribute_id": attribute.id,
                "shopify_id": attribute.shopify_id,
                "name": attribute.name,
                "required": relation.required,
                "values": values,
            }
        )

    return results


def classify_product(
    product,
    category_map=None,
    category_index=None,
):
    """
    Main classification pipeline.

    One product failing does not affect other products.
    """

    product_text = build_product_text(
        product
    )

    image_url = get_product_image_url(
        product
    )

    image_status = (
        "available"
        if image_url
        else "not_available"
    )

    if not product_text.strip():
        return save_result(
            product=product,
            category=None,
            confidence=0.0,
            matched=[],
            alternatives=[],
            attributes=[],
            image_status=image_status,
            status="manual_review",
            review_reason=(
                "Product has insufficient "
                "information for automatic "
                "classification."
            ),
            ai_reason="",
        )

    if (
        category_map is None
        or category_index is None
    ):
        (
            category_map,
            category_index,
        ) = build_category_index()

    candidates = generate_candidates(
        product_text,
        category_map,
        category_index,
    )

    if not candidates:
        return save_result(
            product=product,
            category=None,
            confidence=0.0,
            matched=[],
            alternatives=[],
            attributes=[],
            image_status=image_status,
            status="manual_review",
            review_reason=(
                "No Shopify taxonomy "
                "candidate categories were found."
            ),
            ai_reason="",
        )

    # ---------------------------------------------------------
    # AI CLASSIFICATION
    # ---------------------------------------------------------

    try:
        ai_classifier = TaxonomyAIClassifier()

        ai_result = ai_classifier.classify(
            product_text=product_text,
            categories=candidates,
            level=None,
            image_url=image_url,
        )

    except TaxonomyAIError as exc:
        return save_result(
            product=product,
            category=None,
            confidence=0.0,
            matched=[],
            alternatives=[],
            attributes=[],
            image_status=image_status,
            status="failed",
            review_reason=(
                "AI classification failed. "
                "Product requires retry or manual review."
            ),
            error_message=str(exc),
            ai_reason="",
        )

    if not ai_result:
        return save_result(
            product=product,
            category=None,
            confidence=0.0,
            matched=[],
            alternatives=[],
            attributes=[],
            image_status=image_status,
            status="manual_review",
            review_reason=(
                "AI did not return a classification."
            ),
            ai_reason="",
        )

    selected_category_id = (
        ai_result["category_id"]
    )

    best_category = category_map.get(
        selected_category_id
    )

    if not best_category:
        return save_result(
            product=product,
            category=None,
            confidence=0.0,
            matched=[],
            alternatives=[],
            attributes=[],
            image_status=image_status,
            status="failed",
            review_reason=(
                "AI selected an invalid taxonomy category."
            ),
            error_message=(
                "AI selected category ID "
                f"{selected_category_id}, "
                "which is not present in the candidate map."
            ),
            ai_reason=ai_result.get(
                "reason",
                "",
            ),
        )

    confidence = (
        float(
            ai_result.get(
                "confidence",
                0,
            )
        )
        / 100.0
    )

    confidence = max(
        0.0,
        min(
            confidence,
            1.0,
        ),
    )

    # ---------------------------------------------------------
    # MATCHED TERMS
    # ---------------------------------------------------------

    _, matched = heuristic_score(
        product,
        best_category,
        product_text,
    )

    # ---------------------------------------------------------
    # ALTERNATIVE CATEGORIES
    # ---------------------------------------------------------

    alternative_rows = []

    scored_candidates = []

    for category in candidates:
        if category.id == best_category.id:
            continue

        score, matched_terms = (
            heuristic_score(
                product,
                category,
                product_text,
            )
        )

        scored_candidates.append(
            (
                score,
                category,
                matched_terms,
            )
        )

    scored_candidates.sort(
        key=lambda row: (
            row[0],
            row[1].is_leaf,
            row[1].level,
        ),
        reverse=True,
    )

    for (
        score,
        category,
        matched_terms,
    ) in scored_candidates[
        :MAX_ALTERNATIVES
    ]:
        alternative_rows.append(
            {
                "category_id": category.id,
                "shopify_id": category.shopify_id,
                "name": category.name,
                "full_name": category.full_name,
                "level": category.level,
                "confidence": round(
                    score,
                    4,
                ),
                "matched_terms": matched_terms,
            }
        )

    # ---------------------------------------------------------
    # ATTRIBUTE EXTRACTION
    # ---------------------------------------------------------

    attributes = extract_attributes(
        product,
        best_category,
        product_text,
    )

    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------

    if confidence >= HIGH_CONFIDENCE:
        status = "classified"
        review_reason = ""

    elif confidence >= REVIEW_CONFIDENCE:
        status = "needs_review"
        review_reason = (
            "Classification confidence is below "
            "the automatic approval threshold."
        )

    else:
        status = "manual_review"
        review_reason = (
            "Classification confidence is too low "
            "for automatic approval."
        )

    return save_result(
        product=product,
        category=best_category,
        confidence=confidence,
        matched=matched,
        alternatives=alternative_rows,
        attributes=attributes,
        image_status=image_status,
        status=status,
        review_reason=review_reason,
        ai_reason=ai_result.get(
            "reason",
            "",
        ),
    )


def save_result(
    product,
    category,
    confidence,
    matched,
    alternatives,
    attributes,
    image_status,
    status,
    review_reason="",
    error_message="",
    ai_reason="",
):
    result, _ = (
        ProductTaxonomyResult.objects
        .update_or_create(
            product=product,
            defaults={
                "category": category,
                "confidence": round(
                    max(
                        0.0,
                        min(
                            1.0,
                            confidence,
                        ),
                    ),
                    4,
                ),
                "matched_text": ", ".join(
                    matched or []
                ),
                "alternatives": (
                    alternatives or []
                ),
                "attributes": (
                    attributes or []
                ),
                "image_status": (
                    image_status
                    or "not_available"
                ),
                "status": (
                    status
                    or "pending"
                ),
                "review_reason": (
                    review_reason
                    or ""
                ),
                "error_message": (
                    error_message
                    or ""
                ),
                "ai_reason": (
                    ai_reason
                    or ""
                ),
            },
        )
    )

    return result
