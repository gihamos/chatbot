from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from chatbot.views import register  

urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth Django
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(template_name="registration/login.html"),
        name="logout",
    ),
    path(
        "accounts/register/",
        register,
        name="register",
    ),

    # Routes de l'application chatbot
    path("", include("chatbot.urls")), 
]
