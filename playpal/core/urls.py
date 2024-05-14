from django.urls import path
from .views import (
    post_detail,
    games_view,
    index_page,
    category,
    search,
    post_edit,
    post_delete,
    like_post,
    comment_delete,
)

app_name = "core"
urlpatterns = [
    path("search/", search, name="search"),
    path("index/", index_page, name="index-page"),
    path("games/", games_view, name="games"),
    path("detail_view/<int:pk>", post_detail, name="post-detail"),
    path("edit_post/<int:pk>", post_edit, name="edit-post"),
    path("delete_post/<int:pk>", post_delete, name="delete-post"),
    path(
        "posts/<int:post_pk>/comments/<int:comment_pk>/delete/",
        comment_delete,
        name="comment-delete",
    ),
    path("posts/<int:pk>/like/", like_post, name="like-post"),
    path("<slug:slug>/", category, name="category"),
    ###########################
    # path('post_list', PostListView.as_view(), name='post-list'),
]
