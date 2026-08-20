from django.contrib import admin

from classification.models import (
    ClassificationResult,
    ClassificationCandidate,
)


@admin.register(ClassificationResult)
class ClassificationResultAdmin(admin.ModelAdmin):

    list_display = [
        "product",
        "category",
        "confidence",
        "status",
        "created_at",
    ]

    list_filter = [
        "status",
    ]

    search_fields = [
        "product__title",
        "category__name",
    ]


@admin.register(ClassificationCandidate)
class ClassificationCandidateAdmin(admin.ModelAdmin):

    list_display = [
        "product",
        "category",
        "score",
        "rank",
        "source",
    ]

    list_filter = [
        "source",
    ]

    search_fields = [
        "product__title",
        "category__name",
    ]