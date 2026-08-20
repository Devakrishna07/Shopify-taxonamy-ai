from django.db import models


class TaxonomyCategory(models.Model):
    shopify_id = models.CharField(
        max_length=255,
        unique=True
    )

    name = models.CharField(
        max_length=500
    )

    full_name = models.TextField(
        null=True,
        blank=True
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children"
    )

    level = models.IntegerField(
        default=0
    )

    is_leaf = models.BooleanField(
        default=False
    )

    taxonomy_version = models.CharField(
        max_length=50
    )

    class Meta:
        db_table = "taxonomy_categories"
        indexes = [
            models.Index(fields=["parent"]),
            models.Index(fields=["shopify_id"]),
        ]

    def __str__(self):
        return self.full_name or self.name


class TaxonomyAttribute(models.Model):
    shopify_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=255
    )

    class Meta:
        db_table = "taxonomy_attributes"

    def __str__(self):
        return self.name


class TaxonomyValue(models.Model):
    attribute = models.ForeignKey(
        TaxonomyAttribute,
        on_delete=models.CASCADE,
        related_name="values"
    )

    shopify_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    value = models.CharField(
        max_length=500
    )

    class Meta:
        db_table = "taxonomy_values"

    def __str__(self):
        return self.value


class CategoryAttribute(models.Model):
    category = models.ForeignKey(
        TaxonomyCategory,
        on_delete=models.CASCADE,
        related_name="category_attributes"
    )

    attribute = models.ForeignKey(
        TaxonomyAttribute,
        on_delete=models.CASCADE,
        related_name="attribute_categories"
    )

    class Meta:
        db_table = "category_attributes"
        constraints = [
            models.UniqueConstraint(
                fields=["category", "attribute"],
                name="unique_category_attribute"
            )
        ]

    def __str__(self):
        return f"{self.category} - {self.attribute}"