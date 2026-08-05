"""URL configuration for the sources API."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.sources import views


router = DefaultRouter()
router.register(r"sources", views.KnowledgeSourceViewSet, basename="source")

urlpatterns = [
    path("", include(router.urls)),
    path("sources/<int:pk>/reprocess/", views.reprocess_source, name="source-reprocess"),
]
