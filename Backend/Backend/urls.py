

from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/products/', include('products.urls')),
    path("api/imports/", include("imports.urls")),
    path("api/taxonamy/",include("taxonamy.urls")),
]

