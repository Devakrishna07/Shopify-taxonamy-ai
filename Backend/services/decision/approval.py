from dataclasses import dataclass
from enum import Enum


class ReviewAction(str, Enum):

    APPROVE = "APPROVE"
    EDIT = "EDIT"
    REJECT = "REJECT"
    RECLASSIFY = "RECLASSIFY"


@dataclass
class ApprovalResult:

    action: ReviewAction
    final_category: dict | None
    approved_by: object = None
    comment: str = ""


def approve_result(
    *,
    action,
    ai_category,
    final_category=None,
    approved_by=None,
    comment="",
):
    try:

        review_action = ReviewAction(
            action.upper()
        )

    except (ValueError, AttributeError):

        raise ValueError(
            "Invalid review action. "
            "Use APPROVE, EDIT, REJECT or RECLASSIFY."
        )

    if review_action == ReviewAction.APPROVE:

        if ai_category is None:
            raise ValueError(
                "Cannot approve without an AI category."
            )

        return ApprovalResult(
            action=review_action,
            final_category=ai_category,
            approved_by=approved_by,
            comment=comment,
        )

    if review_action in {
        ReviewAction.EDIT,
        ReviewAction.RECLASSIFY,
    }:

        if final_category is None:
            raise ValueError(
                "final_category is required."
            )

        return ApprovalResult(
            action=review_action,
            final_category=final_category,
            approved_by=approved_by,
            comment=comment,
        )

    return ApprovalResult(
        action=review_action,
        final_category=None,
        approved_by=approved_by,
        comment=comment,
    )