from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Post, Category, Like, Comment
from .forms import CommentForm, PostForm, PostUpdateForm
from django.http import HttpResponse
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from django.contrib.auth.decorators import user_passes_test


def is_post_owner(user):
    """Checks if the user is the owner of the post being deleted, edited etc"""
    pk = user.resolver_match.kwargs.get("pk")
    post = get_object_or_404(Post, id=pk)
    return Post.author == user


@login_required
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


@login_required
def post_detail(request, pk, status=Post.ACTIVE):
    """Renders the post's detailed page"""
    post = get_object_or_404(Post, id=pk)

    try:
        user_liked = Like.objects.filter(post=post, user=request.user).exists()
    except Like.DoesNotExist:
        user_liked = False

    # Get the total number of likes for the post
    like_count = Like.objects.filter(post=post).count()

    # Retrieve the comments for the current post
    comments = Comment.objects.filter(post=post)

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            # Redirect to the same page to display the new comment
            return redirect("core:post-detail", pk=post.id)
    else:
        form = CommentForm()

    context = {
        "post": post,
        "form": form,
        "user_liked": user_liked,
        "like_count": like_count,
        "comments": comments,
    }

    return render(request, "core/post_detail.html", context)


@login_required
def like_post(request, pk, status=Post.ACTIVE):
    """A view function that handles like/unlike actions"""

    try:
        post = get_object_or_404(Post, id=pk)

        if Like.objects.filter(post=post, user=request.user).exists():
            Like.objects.filter(post=post, user=request.user).delete()
        else:
            Like.objects.create(post=post, user=request.user)
        return redirect("core:post-detail", pk=pk)
    except (Post.DoesNotExist, Like.DoesNotExist) as e:
        messages.error(
            request,
            "An error occured while processing your action, please try again later.",
        )
        return redirect("core:post-detail")


@login_required
@user_passes_test(is_post_owner)
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


@login_required
@user_passes_test(is_post_owner)
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


@login_required
@user_passes_test(is_post_owner)
def comment_delete(request, post_pk, comment_pk):
    """A function that deletes a comment"""
    comment = Comment.objects.get(id=comment_pk)
    post = Post.objects.get(id=post_pk)

    if request.method == "POST":
        comment.delete()
        return redirect("core:post-detail", pk=post.id)

    context = {
        "post": post,
        "comment": comment,
    }
    return render(request, "core/delete_comment.html", context)


@login_required
def category(request, slug):
    """Renders the category page"""
    category = get_object_or_404(Category, slug=slug)
    posts = category.posts.filter(status=Post.ACTIVE)

    context = {"category": category, "posts": posts}

    return render(request, "core/category.html", context)


@login_required
def games_view(request):
    """renders the game page"""
    return render(request, "core/games.html")


@login_required
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


# class PostListView(View):
#     def get(self, request, *args, **kwargs):
#         posts = Post.objects.all().order_by('-created_at')

#         context = {
#             'post_list': posts,
#         }

#         return render(request, 'landing/post_list.html', context)
