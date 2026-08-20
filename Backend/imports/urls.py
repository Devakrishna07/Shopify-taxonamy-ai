from django.urls import path

from .views import (
    ImportUploadView,
    ImportDetailView,
)


urlpatterns = [
    path(
        "",
        ImportUploadView.as_view(),
        name="import-upload"
    ),

    path(
        "<int:pk>/",
        ImportDetailView.as_view(),
        name="import-detail"
    ),
]