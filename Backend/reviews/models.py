from django.db import models


class ReviewAction(models.Model):

    APPROVE = "APPROVE"
    EDIT = "EDIT"
    REJECT = "REJECT"

    ACTION_CHOICES = [
        (APPROVE, "Approve"),
        (EDIT, "Edit"),
        (REJECT, "Reject"),
    ]

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="review_actions"
    )

    old_category_id = models.BigIntegerField(
        null=True,
        blank=True
    )

    new_category_id = models.BigIntegerField(
        null=True,
        blank=True
    )

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES
    )

    comment = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product_id} - {self.action}"