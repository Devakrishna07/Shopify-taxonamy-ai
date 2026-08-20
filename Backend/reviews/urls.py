from django.urls import path

from .views import (
    ReviewListView,
    ReviewDetailView,
    ApproveReviewView,
    EditReviewView,
    RejectReviewView,
)


urlpatterns = [

    path(
        "",
        ReviewListView.as_view(),
        name="review-list"
    ),

    path(
        "<int:pk>/",
        ReviewDetailView.as_view(),
        name="review-detail"
    ),

    path(
        "<int:pk>/approve/",
        ApproveReviewView.as_view(),
        name="review-approve"
    ),

    path(
        "<int:pk>/edit/",
        EditReviewView.as_view(),
        name="review-edit"
    ),

    path(
        "<int:pk>/reject/",
        RejectReviewView.as_view(),
        name="review-reject"
    ),
]