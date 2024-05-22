from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from users.views import (
    ProfileView,
    ProfileEditView,
    AddFollowers,
    RemoveFollower,
    UserSearch,
    ListFollowers,
)


urlpatterns = [
    path("search/", UserSearch.as_view(), name="profile-search"),
    path("sign_up/", views.sign_up, name="sign-up"),
    path("profile/<int:pk>/", ProfileView.as_view(), name="profile"),
    path("profile/<int:pk>/edit/", ProfileEditView.as_view(), name="profile-edit"),
    path("profile/<int:pk>/followers", ListFollowers.as_view(), name="list-followers"),
    path("profile/<int:pk>/follower/add", AddFollowers.as_view(), name="add-follower"),
    path(
        "profile/<int:pk>/follower/remove",
        RemoveFollower.as_view(),
        name="remove-follower",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path("logout/", views.logout_view, name="logout"),
    path(
        "reset_password/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html"
        ),
        name="reset_password",
    ),
    path(
        "reset_password_sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset_password_complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete/",
    ),
]
