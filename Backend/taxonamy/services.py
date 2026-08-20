import re

SRS_CATEGORY_MAPPING = {

    "outdoor furniture": [
        "outdoor",
        "patio",
        "garden",
        "deck",
        "outdoor furniture",
        "patio furniture",
    ],

    "living room": [
        "sofa",
        "sectional",
        "couch",
        "coffee table",
        "side table",
        "end table",
        "ottoman",
        "accent chair",
        "living room",
    ],

    "bar and dining": [
        "dining table",
        "dining chair",
        "bar stool",
        "counter stool",
        "bar table",
        "dining",
        "bar",
    ],

    "bathroom": [
        "bathroom",
        "vanity",
        "bath cabinet",
        "bathroom cabinet",
        "medicine cabinet",
    ],

    "lighting": [
        "lamp",
        "lighting",
        "pendant",
        "chandelier",
        "sconce",
        "floor lamp",
        "table lamp",
    ],

    "office furniture": [
        "office",
        "desk",
        "office chair",
        "computer desk",
        "writing desk",
        "filing cabinet",
    ],

    "bedroom": [
        "bed",
        "bedroom",
        "nightstand",
        "dresser",
        "chest",
        "bed frame",
    ],
}


from .models import (
    TaxonomyCategory,
    ProductTaxonomyResult,
)

def srs_category_score(product_text, category):

    score = 0

    category_text = normalize_text(
        category.full_name
    )

    for srs_category, keywords in SRS_CATEGORY_MAPPING.items():

        if srs_category in category_text:

            for keyword in keywords:

                if keyword in product_text:

                    score += 25

    return score



def normalize_text(value):
    if not value:
        return ""

    value = str(value).lower()

    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def get_product_text(product):

    fields = [
        "product_name",
        "name",
        "title",
        "product_description",
        "description",
        "product_category",
        "product_sub_category",
        "materials",
        "bullets",
        "collection_name",
        "product_color",
    ]

    values = []

    for field in fields:
        value = getattr(
            product,
            field,
            None
        )

        if value:
            values.append(
                str(value)
            )

    return normalize_text(
        " ".join(values)
    )


def category_score(product_text, category):

    category_text = normalize_text(
        category.full_name
    )

    category_name = normalize_text(
        category.name
    )

    score = 0

    category_words = set(
        category_text.split()
    )

    product_words = set(
        product_text.split()
    )

    for word in category_words:

        if len(word) < 3:
            continue

        if word in product_words:
            score += 10

    if category_name in product_text:
        score += 30

    return score


def classify_product(product):

    product_text = get_product_text(
        product
    )

    if not product_text:

        result, _ = ProductTaxonomyResult.objects.update_or_create(
            product=product,
            defaults={
                "category": None,
                "confidence": 0,
                "matched_text": "",
                "status": "review",
            }
        )

        return result

    categories = TaxonomyCategory.objects.filter(
        is_archived=False
    )

    best_category = None
    best_score = 0

    for category in categories:

        score = category_score(
            product_text,
            category
        )

        score += srs_category_score(
            product_text,
            category
        )

        if score > best_score:

            best_score = score
            best_category = category

    if not best_category:

        confidence = 0
        status = "review"

    else:

        confidence = min(
            100,
            best_score
        )

        status = (
            "classified"
            if confidence >= 70
            else "review"
        )

    result, _ = ProductTaxonomyResult.objects.update_or_create(
        product=product,
        defaults={
            "category": best_category,
            "confidence": confidence,
            "matched_text": product_text,
            "status": status,
        }
    )

    return result