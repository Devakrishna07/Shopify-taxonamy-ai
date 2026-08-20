from django.contrib import admin

from .models import ReviewAction


@admin.register(ReviewAction)
class ReviewActionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "product",
        "action",
        "old_category_id",
        "new_category_id",
        "created_at",
    )

    list_filter = (
        "action",
        "created_at",
    )

    search_fields = (
        "product__title",
        "comment",
    )