from django.contrib import admin

from .models import ProductAttribute


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'product',
        'attribute',
        'value',
        'confidence',
        'created_at',
    ]

    list_filter = [
        'attribute',
        'value',
    ]

    search_fields = [
        'product__title',
        'attribute__name',
        'value__value',
        'raw_value',
    ]

    ordering = [
        '-confidence',
    ]