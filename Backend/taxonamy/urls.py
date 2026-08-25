
from django.urls import path

from .views import (
    TaxonomyCategoryListAPIView,
    TaxonomySearchAPIView,
    TaxonomyAttributeListAPIView,
    TaxonomyValueListAPIView,
    CategoryAttributeListAPIView,

    ProductTaxonomyListAPIView,
    ProductTaxonomyAPIView,

    ClassifyProductAPIView,
    BulkClassifyProductsAPIView,

    TaxonomyStatsAPIView,

    ApproveProductTaxonomyAPIView,
    RejectProductTaxonomyAPIView,
)


urlpatterns = [
    path(
        "categories/",
        TaxonomyCategoryListAPIView.as_view(),
        name="taxonomy-categories",
    ),

    path(
        "search/",
        TaxonomySearchAPIView.as_view(),
        name="taxonomy-search",
    ),

    path(
        "attributes/",
        TaxonomyAttributeListAPIView.as_view(),
        name="taxonomy-attributes",
    ),

    path(
        "values/",
        TaxonomyValueListAPIView.as_view(),
        name="taxonomy-values",
    ),

    path(
        "categories/<int:category_id>/attributes/",
        CategoryAttributeListAPIView.as_view(),
        name="category-attributes",
    ),

    path(
        "products/",
        ProductTaxonomyListAPIView.as_view(),
        name="product-taxonomy-list",
    ),

    path(
        "products/<int:product_id>/",
        ProductTaxonomyAPIView.as_view(),
        name="product-taxonomy",
    ),

    path(
        "products/<int:product_id>/classify/",
        ClassifyProductAPIView.as_view(),
        name="classify-product",
    ),

    path(
        "products/classify/",
        BulkClassifyProductsAPIView.as_view(),
        name="bulk-classify-products",
    ),

    path(
        "stats/",
        TaxonomyStatsAPIView.as_view(),
        name="taxonomy-stats",
    ),

    path(
        "products/<int:product_id>/approve/",
        ApproveProductTaxonomyAPIView.as_view(),
        name="approve-product-taxonomy",
    ),

    path(
        "products/<int:product_id>/reject/",
        RejectProductTaxonomyAPIView.as_view(),
        name="reject-product-taxonomy",
    ),
]
