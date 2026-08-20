def build_alternatives(
    candidates,
    primary_category_id=None,
    max_results=5,
):
    """
    Normalize, deduplicate and rank AI category alternatives.
    """

    if not isinstance(candidates, list):
        raise ValueError("candidates must be a list.")

    if max_results <= 0:
        return []

    alternatives = []
    seen_category_ids = set()

    for candidate in candidates:

        if not isinstance(candidate, dict):
            continue

        category_id = candidate.get("category_id")
        category_name = candidate.get("category_name")
        confidence = candidate.get("confidence")

        if category_id is None:
            continue

        if category_id == primary_category_id:
            continue

        if category_id in seen_category_ids:
            continue

        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            continue

        if not 0 <= confidence <= 1:
            continue

        if not category_name:
            continue

        seen_category_ids.add(category_id)

        alternatives.append({
            "category_id": category_id,
            "category_name": str(category_name),
            "confidence": confidence,
        })

    alternatives.sort(
        key=lambda item: item["confidence"],
        reverse=True,
    )

    alternatives = alternatives[:max_results]

    for index, alternative in enumerate(
        alternatives,
        start=1,
    ):
        alternative["rank"] = index

    return alternatives