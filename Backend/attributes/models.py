from django.db import models


class ProductAttribute(models.Model):
    """
    Stores an attribute extracted from a product and its
    corresponding Shopify taxonomy value.
    """

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='attributes'
    )

    attribute = models.ForeignKey(
        'taxonamy.TaxonomyAttribute',
        on_delete=models.CASCADE,
        related_name='product_attributes'
    )

    value = models.ForeignKey(
        'taxonamy.TaxonomyValue',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='product_attributes'
    )

    raw_value = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    confidence = models.DecimalField(
        max_digits=6,
        decimal_places=5,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_attributes'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['attribute']),
            models.Index(fields=['value']),
        ]

    def __str__(self):
        value = self.value.value if self.value else self.raw_value

        return (
            f"{self.product_id} - "
            f"{self.attribute.name} - "
            f"{value}"
        )