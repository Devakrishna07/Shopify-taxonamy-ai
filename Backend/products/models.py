from django.db import models


class Product(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("REVIEW", "Review"),
        ("APPROVED", "Approved"),
    ]

    external_product_id = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    sku = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    title = models.TextField()

    description = models.TextField(
        null=True,
        blank=True
    )

    brand = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    product_type = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    existing_category = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    existing_subcategory = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    normalized_text = models.TextField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# productImage model
class ProductImage(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("VALID", "Valid"),
        ("INVALID", "Invalid"),
        ("FAILED", "Failed"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    url = models.TextField()

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    local_path = models.TextField(
        null=True,
        blank=True
    )

    error_message = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product.title} - {self.url}"