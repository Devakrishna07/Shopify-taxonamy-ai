from django.db import models


class ResultViewLog(models.Model):
    """
    Optional lightweight audit record for result API access.
    This does not duplicate classification data.
    """

    product_id = models.BigIntegerField()

    accessed_at = models.DateTimeField(auto_now_add=True)

    endpoint = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["-accessed_at"]

    def __str__(self):
        return f"Product {self.product_id} - {self.accessed_at}"

from django.conf import settings
from django.db import models

from classification.models import ClassificationResult


class ResultViewLog(models.Model):
    """
    Optional lightweight audit record for result API access.
    This does not duplicate classification data.
    """

    product_id = models.BigIntegerField()

    accessed_at = models.DateTimeField(
        auto_now_add=True
    )

    endpoint = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-accessed_at"]

    def __str__(self):
        return (
            f"Product {self.product_id} - "
            f"{self.accessed_at}"
        )


class DecisionReview(models.Model):
    """
    Stores Decision & Review state for an existing
    ClassificationResult.

    The original ClassificationResult is NOT replaced.
    AI prediction data is retained separately.
    """

    AUTO_APPROVED = "AUTO_APPROVED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    FAILED = "FAILED"

    DECISION_STATUS_CHOICES = [
        (
            AUTO_APPROVED,
            "Auto Approved",
        ),
        (
            NEEDS_REVIEW,
            "Needs Review",
        ),
        (
            MANUAL_REVIEW,
            "Manual Review",
        ),
        (
            FAILED,
            "Failed",
        ),
    ]

    APPROVE = "APPROVE"
    EDIT = "EDIT"
    REJECT = "REJECT"
    RECLASSIFY = "RECLASSIFY"

    REVIEW_ACTION_CHOICES = [
        (APPROVE, "Approve"),
        (EDIT, "Edit"),
        (REJECT, "Reject"),
        (RECLASSIFY, "Reclassify"),
    ]

    classification_result = models.OneToOneField(
        ClassificationResult,
        on_delete=models.CASCADE,
        related_name="decision_review",
    )

    # Immutable AI snapshot
    ai_prediction = models.JSONField(
        default=dict,
        blank=True,
    )

    ai_confidence = models.FloatField(
        default=0.0,
    )

    ai_alternatives = models.JSONField(
        default=list,
        blank=True,
    )

    decision_status = models.CharField(
        max_length=30,
        choices=DECISION_STATUS_CHOICES,
        default=FAILED,
    )

    requires_review = models.BooleanField(
        default=False,
    )

    decision_reason = models.TextField(
        blank=True,
        default="",
    )

    # Human-approved/final result
    final_category_id = models.BigIntegerField(
        null=True,
        blank=True,
    )

    review_action = models.CharField(
        max_length=20,
        choices=REVIEW_ACTION_CHOICES,
        null=True,
        blank=True,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_classification_decisions",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    review_comment = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return (
            f"Decision for ClassificationResult "
            f"{self.classification_result_id}: "
            f"{self.decision_status}"
        )