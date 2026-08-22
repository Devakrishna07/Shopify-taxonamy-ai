from django.urls import path

from classification.views import (
    ProductClassificationView,
    ClassificationResultView,
    ImportClassificationView,
)


urlpatterns = [
    path(
        "products/<int:product_id>/classify/",
        ProductClassificationView.as_view(),
        name="classify-product",
    ),

    path(
        "classifications/<int:product_id>/",
        ClassificationResultView.as_view(),
        name="classification-result",
    ),

    path(
        "imports/<int:import_id>/classify/",
        ImportClassificationView.as_view(),
        name="classify-import",
    ),
]