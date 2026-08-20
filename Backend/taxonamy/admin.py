from django.contrib import admin

from .models import (
    TaxonomyCategory,
    TaxonomyAttribute,
    TaxonomyValue,
    CategoryAttribute,
    ProductTaxonomyResult,
)


@admin.register(TaxonomyCategory)
class TaxonomyCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "shopify_id",
        "name",
        "full_name",
        "level",
        "is_root",
        "is_leaf",
    )

    search_fields = (
        "shopify_id",
        "name",
        "full_name",
    )

    list_filter = (
        "level",
        "is_root",
        "is_leaf",
        "is_archived",
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
        "name",
        "attribute",
    )

    search_fields = (
        "shopify_id",
        "name",
    )


@admin.register(CategoryAttribute)
class CategoryAttributeAdmin(admin.ModelAdmin):

    list_display = (
        "category",
        "attribute",
        "required",
    )

    list_filter = (
        "required",
    )


@admin.register(ProductTaxonomyResult)
class ProductTaxonomyResultAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "category",
        "confidence",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "product__id",
        "matched_text",
    )