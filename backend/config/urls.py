from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from django.conf    import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/users/',  include('apps.users.urls')),
    path('api/posts/',  include('apps.posts.urls')),
    path('api/follows/',include('apps.follows.urls')),
    path('api/likes/',  include('apps.likes.urls')),
    # OpenAPI schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('api/swagger/', SpectacularSwaggerView.as_view(
        url_name='schema'
    ), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)