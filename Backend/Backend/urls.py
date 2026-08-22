

from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/products/', include('products.urls')),
    path("api/imports/", include("imports.urls")),
    path("api/taxonomy/",include("taxonamy.urls")),
    path("api/classification/", include("classification.urls")),
     path('api/attributes/',include('attributes.urls')),
     path("api/reviews/",include("reviews.urls")),
      path("api/processing/",include("processing.urls")),
    path("api/results/",include("results.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

