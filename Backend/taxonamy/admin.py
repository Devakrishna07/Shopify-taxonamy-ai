from django.contrib import admin

from .models import (
    TaxonomyCategory,
    TaxonomyAttribute,
    TaxonomyValue,
    CategoryAttribute,
)


@admin.register(TaxonomyCategory)
class TaxonomyCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "shopify_id",
        "name",
        "parent",
        "level",
        "is_leaf",
        "taxonomy_version",
    )

    search_fields = (
        "shopify_id",
        "name",
        "full_name",
    )

    list_filter = (
        "is_leaf",
        "taxonomy_version",
    )


@admin.register(TaxonomyAttribute)
class TaxonomyAttributeAdmin(admin.ModelAdmin):
    list_display = (
        "shopify_id",
        "name",
    )

    search_fields = (
        "shopify_id",
        "name",
    )


@admin.register(TaxonomyValue)
class TaxonomyValueAdmin(admin.ModelAdmin):
    list_display = (
        "shopify_id",
        "attribute",
        "value",
    )

    search_fields = (
        "shopify_id",
        "value",
    )

    list_filter = (
        "attribute",
    )


@admin.register(CategoryAttribute)
class CategoryAttributeAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "attribute",
    )

    search_fields = (
        "category__name",
        "attribute__name",
    )