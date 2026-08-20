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