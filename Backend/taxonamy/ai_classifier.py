
import json
import os

from openai import OpenAI


class TaxonomyAIError(Exception):
    pass


class TaxonomyAIClassifier:
    """
    AI-powered Shopify taxonomy classifier.

    The classifier is deliberately restricted to the taxonomy
    candidates supplied by the backend. The AI cannot invent
    a category outside the candidate set.
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise TaxonomyAIError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI(api_key=api_key)

        self.model = os.getenv(
            "TAXONOMY_AI_MODEL",
            "gpt-4.1-mini",
        )

    def classify(
        self,
        product_text,
        categories,
        level=None,
        image_url=None,
    ):
        categories = list(categories)

        if not categories:
            return None

        candidate_data = []

        for category in categories:
            candidate_data.append(
                {
                    "id": category.id,
                    "shopify_id": category.shopify_id,
                    "name": category.name,
                    "full_name": category.full_name,
                    "level": category.level,
                    "parent_id": category.parent_id,
                    "is_root": category.is_root,
                    "is_leaf": category.is_leaf,
                }
            )

        prompt = f"""
You are an expert Shopify product taxonomy classifier.

Classify the supplied product into the SINGLE most appropriate
Shopify taxonomy category from the supplied candidate categories.

Taxonomy level:
{level if level is not None else "Use the most appropriate level."}

IMPORTANT RULES:

1. You MUST select one category from the candidate list.
2. NEVER invent a category.
3. NEVER return an ID that is not in the candidate list.
4. Use all available product information.
5. Give the highest importance to the product title and product type.
6. Use the description, brand, existing category and subcategory
   when available.
7. Use the product image when it is available.
8. Missing descriptions must not automatically cause failure.
9. Missing images must not automatically cause failure.
10. Do not classify based on a single weak keyword match.
11. Prefer the most semantically specific category.
12. Prefer a leaf category when the product information supports it.
13. Return JSON only.

PRODUCT INFORMATION:

{product_text}

CANDIDATE TAXONOMY CATEGORIES:

{json.dumps(
    candidate_data,
    indent=2,
    ensure_ascii=False,
)}

Return exactly:

{{
    "category_id": <integer>,
    "confidence": <number from 0 to 100>,
    "reason": "<short explanation>"
}}
"""

        content = [
            {
                "type": "input_text",
                "text": prompt,
            }
        ]

        if image_url:
            content.append(
                {
                    "type": "input_image",
                    "image_url": image_url,
                }
            )

        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
            )

        except Exception as exc:
            raise TaxonomyAIError(
                f"AI request failed: {exc}"
            ) from exc

        raw = (
            getattr(response, "output_text", "")
            or ""
        ).strip()

        if not raw:
            raise TaxonomyAIError(
                "AI returned an empty response."
            )

        if raw.startswith("```"):
            raw = raw.replace(
                "```json",
                "",
            )
            raw = raw.replace(
                "```",
                "",
            )
            raw = raw.strip()

        try:
            result = json.loads(raw)

        except json.JSONDecodeError as exc:
            raise TaxonomyAIError(
                f"AI returned invalid JSON: {raw}"
            ) from exc

        try:
            category_id = int(
                result.get("category_id")
            )
        except (
            TypeError,
            ValueError,
        ):
            raise TaxonomyAIError(
                "AI did not return a valid category_id."
            )

        try:
            confidence = float(
                result.get("confidence", 0)
            )
        except (
            TypeError,
            ValueError,
        ):
            confidence = 0

        confidence = max(
            0,
            min(confidence, 100),
        )

        valid_ids = {
            category.id
            for category in categories
        }

        if category_id not in valid_ids:
            raise TaxonomyAIError(
                "AI selected a category that was not "
                "provided as a candidate."
            )

        return {
            "category_id": category_id,
            "confidence": confidence,
            "reason": str(
                result.get("reason", "")
            ),
        }