from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_view, name="chat"),
    path("send/", views.send_message, name="send_message"),
    # Gestion des conversations
    path("conversation/new/", views.new_conversation, name="new_conversation"),
    path("conversation/<int:pk>/switch/", views.switch_conversation, name="switch_conversation"),
    path("conversation/<int:pk>/delete/", views.delete_conversation, name="delete_conversation"),
]
