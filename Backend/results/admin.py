from django.contrib import admin

from .models import ResultViewLog


@admin.register(ResultViewLog)
class ResultViewLogAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "product_id",
        "endpoint",
        "accessed_at",
    ]

    list_filter = [
        "accessed_at",
    ]

    search_fields = [
        "product_id",
        "endpoint",
    ]