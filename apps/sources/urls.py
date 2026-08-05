"""URL configuration for the sources app."""

from django.urls import path

from apps.sources import views


app_name = "sources"

urlpatterns = [
    path("", views.source_list, name="source_list"),
    path("add/", views.add_source, name="add_source"),
]
