from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from users.views import ProfileView, ProfileEditView, AddFollowers, RemoveFollower

app_name = "users"
urlpatterns = [
    path("sign_up/", views.sign_up, name="sign-up"),
    path("profile/<int:pk>/", ProfileView.as_view(), name="profile"),
    path("profile/<int:pk>/edit/", ProfileEditView.as_view(), name="profile-edit"),
    path("profile/<int:pk>/follower/add", AddFollowers.as_view(), name="add-follower"),
    path("profile/<int:pk>/follower/remove", RemoveFollower.as_view(), name="remove-follower"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path("logout/", views.logout_view, name="logout"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="landing/password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "password_reset_done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="landing/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="landing/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset_complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="landing/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
