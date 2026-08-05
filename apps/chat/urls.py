from django.urls import path

from apps.chat import views


app_name = "chat"

urlpatterns = [
    path("", views.conversation_list, name="conversation_list"),
    path("new/", views.new_conversation, name="new_conversation"),
    path("<int:pk>/", views.conversation_detail, name="conversation_detail"),
    path("<int:pk>/ask/", views.ask, name="ask"),
]
