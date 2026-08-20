from dataclasses import dataclass
from enum import Enum


class DecisionStatus(str, Enum):
    AUTO_APPROVED = "AUTO_APPROVED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    FAILED = "FAILED"


@dataclass(frozen=True)
class ConfidencePolicy:
    auto_approve_threshold: float = 0.85
    review_threshold: float = 0.60

    def __post_init__(self):
        if not 0 <= self.review_threshold <= 1:
            raise ValueError(
                "review_threshold must be between 0 and 1."
            )

        if not 0 <= self.auto_approve_threshold <= 1:
            raise ValueError(
                "auto_approve_threshold must be between 0 and 1."
            )

        if self.review_threshold > self.auto_approve_threshold:
            raise ValueError(
                "review_threshold cannot be greater than "
                "auto_approve_threshold."
            )


def evaluate_confidence(
    confidence,
    policy=None,
):
    """
    Decision policy:

        >= 0.85 -> AUTO_APPROVED
        >= 0.60 -> NEEDS_REVIEW
        <  0.60 -> MANUAL_REVIEW
    """

    policy = policy or ConfidencePolicy()

    if confidence is None:
        raise ValueError("confidence is required.")

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        raise ValueError("confidence must be numeric.")

    if not 0 <= confidence <= 1:
        raise ValueError(
            "confidence must be between 0 and 1."
        )

    if confidence >= policy.auto_approve_threshold:
        return DecisionStatus.AUTO_APPROVED

    if confidence >= policy.review_threshold:
        return DecisionStatus.NEEDS_REVIEW

    return DecisionStatus.MANUAL_REVIEW