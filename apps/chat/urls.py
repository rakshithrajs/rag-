"""URL configuration for the chat API."""

from django.urls import path

from apps.chat import views


urlpatterns = [
    path("conversations/", views.conversation_list_create, name="conversation_list_create"),
    path("conversations/<int:pk>/", views.conversation_detail, name="conversation_detail"),
    path("conversations/<int:pk>/ask/", views.ask, name="ask"),
]
