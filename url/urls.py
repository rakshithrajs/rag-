from django.contrib import admin
from django.urls import path

from urloader import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("summary/", views.summary, name="summary"),
    path("test-ollama/", views.test_ollama, name="test_ollama"),
]
