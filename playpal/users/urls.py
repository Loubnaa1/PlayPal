from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "users"
urlpatterns = [
    path("sign_up/", views.sign_up, name="sign-up"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path("logout/", views.logout_view, name="logout"),
    path("profile", views.user_profile, name="profile"),
]
