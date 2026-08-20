from django.db import models


class TaxonomyCategory(models.Model):
    shopify_id = models.CharField(
        max_length=255,
        unique=True
    )

    name = models.CharField(
        max_length=255,
        default=""
    )

    full_name = models.TextField(
        blank=True,
        default=""
    )

    parent_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default=None
    )

    level = models.PositiveIntegerField(
        default=0
    )

    is_root = models.BooleanField(
        default=False
    )

    is_leaf = models.BooleanField(
        default=False
    )

    is_archived = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "taxonomy_categories"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name or self.name


class TaxonomyAttribute(models.Model):
    shopify_id = models.CharField(
        max_length=255,
        unique=True
    )

    name = models.CharField(
        max_length=255,
        default=""
    )

    description = models.TextField(
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "taxonomy_attributes"
        ordering = ["name"]

    def __str__(self):
        return self.name


class TaxonomyValue(models.Model):
    shopify_id = models.CharField(
        max_length=255,
        unique=True
    )

    attribute = models.ForeignKey(
        TaxonomyAttribute,
        on_delete=models.CASCADE,
        related_name="values"
    )

    name = models.CharField(
        max_length=255,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
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
        related_name="category_attributes"
    )

    attribute = models.ForeignKey(
        TaxonomyAttribute,
        on_delete=models.CASCADE,
        related_name="category_attributes"
    )

    required = models.BooleanField(
        default=False
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
    product = models.OneToOneField(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="taxonomy_result"
    )

    category = models.ForeignKey(
        TaxonomyCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    confidence = models.FloatField(
        default=0.0
    )

    matched_text = models.TextField(
        blank=True,
        default=""
    )

    status = models.CharField(
        max_length=30,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "product_taxonomy_results"

    def __str__(self):
        return f"{self.product_id} - {self.category}"