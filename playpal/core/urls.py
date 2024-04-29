from django.urls import path
from .views import index_view, games_view, post_view

app_name = "core"
urlpatterns = [
    path("", index_view, name="index-page"),
    path("games/", games_view, name="games"),
    path("post_detail/", post_view, name="post-detail"),
]
