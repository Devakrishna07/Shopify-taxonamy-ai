from django.db import models


class ClassificationResult(models.Model):
    STATUS_CHOICES = [
        ("CLASSIFIED", "Classified"),
        ("REVIEW", "Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    product = models.OneToOneField(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="classification_result",
    )

    category = models.ForeignKey(
        "taxonamy.TaxonomyCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classification_results",
    )

    confidence = models.DecimalField(
        max_digits=6,
        decimal_places=5,
        default=0,
    )

    text_score = models.DecimalField(
        max_digits=6,
        decimal_places=5,
        null=True,
        blank=True,
    )

    image_score = models.DecimalField(
        max_digits=6,
        decimal_places=5,
        null=True,
        blank=True,
    )

    attribute_score = models.DecimalField(
        max_digits=6,
        decimal_places=5,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="CLASSIFIED",
    )

    reason = models.TextField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["confidence"],
                name="class_result_conf_idx",
            ),
            models.Index(
                fields=["status"],
                name="class_result_status_idx",
            ),
        ]

    def __str__(self):
        return f"{self.product_id} - {self.category_id}"


class ClassificationCandidate(models.Model):
    SOURCE_CHOICES = [
        ("RULE", "Rule"),
        ("SEMANTIC", "Semantic"),
        ("IMAGE", "Image"),
        ("LLM", "LLM"),
        ("COMBINED", "Combined"),
    ]

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="classification_candidates",
    )

    category = models.ForeignKey(
        "taxonamy.TaxonomyCategory",
        on_delete=models.CASCADE,
        related_name="classification_candidates",
    )

    score = models.DecimalField(
        max_digits=6,
        decimal_places=5,
        default=0,
    )

    rank = models.PositiveIntegerField()

    source = models.CharField(
        max_length=50,
        choices=SOURCE_CHOICES,
        default="COMBINED",
    )

    class Meta:
        ordering = ["rank"]

        indexes = [
            models.Index(
                fields=["product", "rank"],
                name="class_candidate_prod_rank_idx",
            ),
            models.Index(
                fields=["category"],
                name="class_candidate_category_idx",
            ),
        ]

    def __str__(self):
        return f"{self.product_id} - {self.category.name} - {self.score}"