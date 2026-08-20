from django.urls import path

from .views import ProductAttributeView


urlpatterns = [
    path(
        '<int:product_id>/',
        ProductAttributeView.as_view(),
        name='product-attributes'
    ),
]