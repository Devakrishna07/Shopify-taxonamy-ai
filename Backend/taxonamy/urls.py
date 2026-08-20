from django.urls import path

from .views import (
    TaxonomyCategoryListAPIView,
    TaxonomySearchAPIView,
    ProductTaxonomyAPIView,
    ClassifyProductAPIView,
    BulkClassifyProductsAPIView,
)


urlpatterns = [

    path(
        "categories/",
        TaxonomyCategoryListAPIView.as_view(),
        name="taxonomy-categories"
    ),

    path(
        "search/",
        TaxonomySearchAPIView.as_view(),
        name="taxonomy-search"
    ),

    path(
        "products/<int:product_id>/",
        ProductTaxonomyAPIView.as_view(),
        name="product-taxonomy"
    ),

    path(
        "products/<int:product_id>/classify/",
        ClassifyProductAPIView.as_view(),
        name="classify-product"
    ),

    path(
        "products/classify/",
        BulkClassifyProductsAPIView.as_view(),
        name="bulk-classify"
    ),
]