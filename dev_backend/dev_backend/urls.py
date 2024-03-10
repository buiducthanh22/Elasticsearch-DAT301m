from django.urls import include, path
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers

from appsearch.views import ImageViewSet
from appsearch.views import SearchView
from appsearch import views

# Create a router for the API views
router = routers.DefaultRouter()
router.register('upload', ImageViewSet)

# Define URL patterns for the application
urlpatterns = [
    # Include API URLs
    path('', include(router.urls)),
    # Admin panel URLs
    path('admin/', admin.site.urls),
    # Search API endpoint
    path('api/search/', SearchView.as_view(), name='api-search'),
    # Health check endpoint
    path('healthcheck', views.health_check, name='health_check'),
]

# Serve static files if in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
