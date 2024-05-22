from django.urls import path
from .views import (
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
    CreateThread,
    ListThread,
    ThreadView,
    CreateMessage,
    ThreadNotification,
    SharedPost,
    TrendingGamesView,
    Explore,
)

app_name = "core"
urlpatterns = [
    path("index/", PostListView.as_view(), name="index-page"),
    path("trending-games/", TrendingGamesView.as_view(), name="trending-games"),
    # Messages
    path("inbox/", ListThread.as_view(), name="inbox"),
    path("inbox/create-thread/", CreateThread.as_view(), name="create-thread"),
    path("inbox/<int:pk>/", ThreadView.as_view(), name="thread"),
    path(
        "inbox/<int:pk>/create-message/", CreateMessage.as_view(), name="create-message"
    ),
    # Posts & Comments
    path("post/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("post/edit/<int:pk>/", PostEditView.as_view(), name="edit-post"),
    path("post/delete/<int:pk>/", PostDeleteView.as_view(), name="delete-post"),
    path("core/explore/", Explore.as_view(), name="explore"),
    path(
        "inbox/<int:pk>/create-message/", CreateMessage.as_view(), name="create-message"
    ),
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
    path("<slug:slug>/", category, name="category"),
    path("post/<int:pk>/share", SharedPost.as_view(), name="share-post"),
    # Notifications
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
    path(
        "notification/<int:notification_pk>/thread/<int:object_pk>",
        ThreadNotification.as_view(),
        name="thread-notification",
    ),
]
