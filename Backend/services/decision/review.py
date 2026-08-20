from dataclasses import dataclass

from .confidence import (
    DecisionStatus,
    evaluate_confidence,
)

from .alternatives import (
    build_alternatives,
)


@dataclass
class DecisionResult:

    status: DecisionStatus
    confidence: float
    primary_category: dict | None
    alternatives: list
    requires_review: bool
    reason: str


def make_decision(
    *,
    primary_category,
    confidence,
    alternatives=None,
    inference_failed=False,
    policy=None,
):
    """
    Convert AI inference output into a DecisionResult.
    """

    if inference_failed:

        return DecisionResult(
            status=DecisionStatus.FAILED,
            confidence=0.0,
            primary_category=primary_category,
            alternatives=[],
            requires_review=False,
            reason="AI inference failed.",
        )

    if primary_category is None:

        return DecisionResult(
            status=DecisionStatus.FAILED,
            confidence=0.0,
            primary_category=None,
            alternatives=[],
            requires_review=False,
            reason="No primary category was produced.",
        )

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        raise ValueError(
            "confidence must be numeric."
        )

    status = evaluate_confidence(
        confidence,
        policy=policy,
    )

    primary_category_id = (
        primary_category.get("category_id")
        if isinstance(primary_category, dict)
        else None
    )

    normalized_alternatives = build_alternatives(
        alternatives or [],
        primary_category_id=primary_category_id,
    )

    if status == DecisionStatus.AUTO_APPROVED:

        reason = (
            "Confidence meets the automatic "
            "approval threshold."
        )

        requires_review = False

    elif status == DecisionStatus.NEEDS_REVIEW:

        reason = (
            "Confidence requires review before "
            "final approval."
        )

        requires_review = True

    else:

        reason = (
            "Confidence is below the review threshold."
        )

        requires_review = True

    return DecisionResult(
        status=status,
        confidence=confidence,
        primary_category=primary_category,
        alternatives=normalized_alternatives,
        requires_review=requires_review,
        reason=reason,
    )