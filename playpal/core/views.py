from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Like
from .forms import CommentForm, PostForm, PostUpdateForm
from django.http import HttpResponse
from django.utils.text import slugify

# Create your views here.


def index_page(request):
    """renders the front page"""
    posts = Post.objects.filter(status=Post.ACTIVE)

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()
            return redirect("core:post-detail", pk=instance.id)
    else:
        form = PostForm()

    context = {
        "posts": posts,
        "form": form,
    }

    return render(request, "core/index.html", context)


def post_detail(request, pk, status=Post.ACTIVE):
    """renders the post's detailed page"""

    post = get_object_or_404(Post, id=pk)

    if request.method == "POST":
        if 'like' in request.POST:
            like, created = Like.objects.get_or_create(user=request.user, post=post)
            if not created:
                like.delete()
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()

            return redirect("core:post-detail", pk=post.id)
    else:
        form = CommentForm()

    context = {"post": post, "form": form}

    return render(request, "core/post_detail.html", context)


def post_edit(request, pk, status=Post.ACTIVE):

    post = get_object_or_404(Post, id=pk)
    if request.method == "POST":
        form = PostUpdateForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("core:post-detail", pk=post.id)
    else:
        form = PostUpdateForm(instance=post)

    context = {"post": post, "form": form}

    return render(request, "core/post_edit.html", context)


def post_delete(request, pk, status=Post.ACTIVE):
    """A function that deletes a post"""

    post = Post.objects.get(id=pk)
    if request.method == "POST":
        post.delete()
        return redirect("core:index-page")
    context = {
        "post": post,
    }

    return render(request, "core/delete_post.html", context)


def category(request, slug):
    """Renders the category page"""
    category = get_object_or_404(Category, slug=slug)
    posts = category.posts.filter(status=Post.ACTIVE)

    context = {"category": category, "posts": posts}

    return render(request, "core/category.html", context)


def games_view(request):
    """renders the game page"""
    return render(request, "core/games.html")


def search(request):
    """The search function"""
    query = request.GET.get("query", "")

    posts = Post.objects.filter(status=Post.ACTIVE).filter(
        Q(title__icontains=query)
        | Q(intro__icontains=query)
        | Q(content__icontains=query)
    )
    context = {"posts": posts, "query": query}

    return render(request, "core/search.html", context)


def robots_txt(request):
    """"""
    text = [
        "User-Agent: *",
        "Disallow: /admin/",
    ]

    return HttpResponse("\n".join(text), content_type="text/plain")
