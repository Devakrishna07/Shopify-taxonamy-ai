from django.urls import path

from .views import (
    ResultsListView,
    ResultDetailView,
    ProductResultView,
    ResultsSummaryView,
)


urlpatterns = [

    path(
        "",
        ResultsListView.as_view(),
        name="results-list"
    ),

    path(
        "<int:pk>/",
        ResultDetailView.as_view(),
        name="result-detail"
    ),

    path(
        "product/<int:product_id>/",
        ProductResultView.as_view(),
        name="product-result"
    ),

    path(
        "summary/",
        ResultsSummaryView.as_view(),
        name="results-summary"
    ),

]