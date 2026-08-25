
from django.db import models


class TaxonomyCategory(models.Model):
    shopify_id = models.CharField(
        max_length=255,
        unique=True,
    )

    name = models.CharField(
        max_length=255,
        default="",
    )

    full_name = models.TextField(
        blank=True,
        default="",
    )

    parent_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default=None,
    )

    level = models.PositiveIntegerField(
        default=0,
    )

    is_root = models.BooleanField(
        default=False,
    )

    is_leaf = models.BooleanField(
        default=False,
    )

    is_archived = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "taxonomy_categories"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name or self.name


class TaxonomyAttribute(models.Model):
    shopify_id = models.CharField(
        max_length=255,
        unique=True,
    )

    name = models.CharField(
        max_length=255,
        default="",
    )

    description = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "taxonomy_attributes"
        ordering = ["name"]

    def __str__(self):
        return self.name


class TaxonomyValue(models.Model):
    shopify_id = models.CharField(
        max_length=255,
        unique=True,
    )

    attribute = models.ForeignKey(
        TaxonomyAttribute,
        on_delete=models.CASCADE,
        related_name="values",
    )

    name = models.CharField(
        max_length=255,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "taxonomy_values"
        ordering = ["name"]

    def __str__(self):
        return self.name


class CategoryAttribute(models.Model):
    category = models.ForeignKey(
        TaxonomyCategory,
        on_delete=models.CASCADE,
        related_name="category_attributes",
    )

    attribute = models.ForeignKey(
        TaxonomyAttribute,
        on_delete=models.CASCADE,
        related_name="category_attributes",
    )

    required = models.BooleanField(
        default=False,
    )

    class Meta:
        db_table = "category_attributes"

        unique_together = (
            "category",
            "attribute",
        )

    def __str__(self):
        return f"{self.category} - {self.attribute}"


class ProductTaxonomyResult(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("classified", "Classified"),
        ("needs_review", "Needs Review"),
        ("manual_review", "Manual Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("failed", "Failed"),
    ]

    IMAGE_STATUS_CHOICES = [
        ("available", "Available"),
        ("not_available", "Not Available"),
        ("invalid", "Invalid"),
    ]

    product = models.OneToOneField(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="taxonomy_result",
    )

    category = models.ForeignKey(
        TaxonomyCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product_taxonomy_results",
    )

    confidence = models.FloatField(
        default=0.0,
    )

    matched_text = models.TextField(
        blank=True,
        default="",
    )

    alternatives = models.JSONField(
        default=list,
        blank=True,
    )

    attributes = models.JSONField(
        default=list,
        blank=True,
    )

    image_status = models.CharField(
        max_length=30,
        choices=IMAGE_STATUS_CHOICES,
        default="not_available",
    )

    review_reason = models.TextField(
        blank=True,
        default="",
    )

    error_message = models.TextField(
        blank=True,
        default="",
    )

    ai_reason = models.TextField(
        blank=True,
        default="",
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "product_taxonomy_results"
        indexes = [
            models.Index(
                fields=["status"],
                name="taxonomy_status_idx",
            ),
            models.Index(
                fields=["confidence"],
                name="taxonomy_conf_idx",
            ),
            models.Index(
                fields=["category"],
                name="taxonomy_category_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.product_id} - "
            f"{self.category}"
        )
