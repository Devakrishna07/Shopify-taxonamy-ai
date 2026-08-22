from django.urls import path

from .views import (
    TaxonomyCategoryListAPIView,
    TaxonomySearchAPIView,
    TaxonomyAttributeListAPIView,
    TaxonomyValueListAPIView,
    CategoryAttributeListAPIView,
    ProductTaxonomyAPIView,
    ClassifyProductAPIView,
    BulkClassifyProductsAPIView,
)


urlpatterns = [

    # ========================================================
    # CATEGORIES
    # ========================================================

    path(
        "categories/",
        TaxonomyCategoryListAPIView.as_view(),
        name="taxonomy-categories",
    ),

    # ========================================================
    # SEARCH
    # ========================================================

    path(
        "search/",
        TaxonomySearchAPIView.as_view(),
        name="taxonomy-search",
    ),

    # ========================================================
    # ATTRIBUTES
    # ========================================================

    path(
        "attributes/",
        TaxonomyAttributeListAPIView.as_view(),
        name="taxonomy-attributes",
    ),

    # ========================================================
    # VALUES
    # ========================================================

    path(
        "values/",
        TaxonomyValueListAPIView.as_view(),
        name="taxonomy-values",
    ),

    # ========================================================
    # CATEGORY ATTRIBUTES
    # ========================================================

    path(
        "categories/<int:category_id>/attributes/",
        CategoryAttributeListAPIView.as_view(),
        name="category-attributes",
    ),

    # ========================================================
    # PRODUCT TAXONOMY
    # ========================================================

    path(
        "products/<int:product_id>/",
        ProductTaxonomyAPIView.as_view(),
        name="product-taxonomy",
    ),

    # ========================================================
    # SINGLE PRODUCT CLASSIFICATION
    # ========================================================

    path(
        "products/<int:product_id>/classify/",
        ClassifyProductAPIView.as_view(),
        name="classify-product",
    ),

    # ========================================================
    # BULK CLASSIFICATION
    # ========================================================

    path(
        "products/classify/",
        BulkClassifyProductsAPIView.as_view(),
        name="bulk-classify",
    ),
]