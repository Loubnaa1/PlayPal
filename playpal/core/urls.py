from django.urls import path
from .views import (
    games_view,
    category,
    CommentDeleteView,
    AddLike,
    Dislike,
    AddCommentLike,
    PostListView,
    PostDetailView,
    PostEditView,
    PostDeleteView,
    CommentReplyView,
    PostNotification,
    FollowNotification,
    RemoveNotification,
)

app_name = "core"
urlpatterns = [
    # path("search/", search, name="search"),
    path("index/", PostListView.as_view(), name="index-page"),
    path("post/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("post/edit/<int:pk>/", PostEditView.as_view(), name="edit-post"),
    path("post/delete/<int:pk>/", PostDeleteView.as_view(), name="delete-post"),
    path(
        "post/<int:post_pk>/comment/<int:pk>/delete/",
        CommentDeleteView.as_view(),
        name="comment-delete",
    ),
    path(
        "post/<int:post_pk>/comment/<int:pk>/like",
        AddCommentLike.as_view(),
        name="comment-like",
    ),
    path("post/<int:pk>/like", AddLike.as_view(), name="likes"),
    path("post/<int:pk>/dislike", Dislike.as_view(), name="dislike"),
    path("games/", games_view, name="games"),
    path("<slug:slug>/", category, name="category"),
    path(
        "notification/<int:notification_pk>/post/<int:post_pk>",
        PostNotification.as_view(),
        name="post-notification",
    ),
    path(
        "notification/<int:notification_pk>/profile/<int:profile_pk>",
        FollowNotification.as_view(),
        name="follow-notification",
    ),
    path(
        "notification/delete/<int:notification_pk>",
        RemoveNotification.as_view(),
        name="notification-delete",
    ),
]
