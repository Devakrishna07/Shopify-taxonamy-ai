from django.urls import path

from .views import TaxonomySearchView


urlpatterns = [
    path(
        "search/",
        TaxonomySearchView.as_view(),
        name="taxonomy-search",
    ),
]