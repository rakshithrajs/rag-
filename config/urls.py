from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

api_v1_patterns = [
    path("sources/", include("apps.sources.urls")),
    path("chat/", include("apps.chat.urls")),
]

urlpatterns = [
    path("api/v1/", include(api_v1_patterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
