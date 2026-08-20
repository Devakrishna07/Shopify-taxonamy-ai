from django.urls import path

from .views import (
    ProcessingJobListCreateView,
    ProcessingJobDetailView,
    ProcessingJobStartView,
)


urlpatterns = [

    path(
        "",
        ProcessingJobListCreateView.as_view(),
        name="processing-jobs"
    ),

    path(
        "<int:pk>/",
        ProcessingJobDetailView.as_view(),
        name="processing-job-detail"
    ),

    path(
        "<int:pk>/start/",
        ProcessingJobStartView.as_view(),
        name="processing-job-start"
    ),
]