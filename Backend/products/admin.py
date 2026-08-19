from django.contrib import admin

from .models import Product, ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "title",
        "sku",
        "brand",
        "product_type",
        "status",
        "created_at",
    ]

    list_filter = [
        "status",
        "brand",
        "product_type",
    ]

    search_fields = [
        "title",
        "sku",
        "brand",
        "product_type",
    ]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "product",
        "status",
        "created_at",
    ]

    list_filter = [
        "status",
    ]