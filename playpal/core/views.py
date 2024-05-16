from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Post, Category, Comment
from .forms import CommentForm, PostForm, PostUpdateForm
from django.http import HttpResponse
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.views import View
from users.models import ProfileModel


def is_post_owner(user):
    """Checks if the user is the owner of the post being deleted, edited etc"""
    pk = user.resolver_match.kwargs.get("pk")
    post = get_object_or_404(Post, id=pk)
    return post.author == user


# @login_required
# def index_page(request):
#     """renders the front page"""
#     logged_in_user = request.user
#     posts = Post.objects.filter(
#         Q(status=Post.ACTIVE, author__profile__followers__in=[logged_in_user.id])
#         | Q(status=Post.ACTIVE, author=logged_in_user)
#     )

#     if request.method == "POST":
#         form = PostForm(request.POST, request.FILES)
#         if form.is_valid():
#             instance = form.save(commit=False)
#             instance.author = request.user
#             instance.save()
#             return redirect("core:post-detail", pk=instance.id)
#     else:
#         form = PostForm()

#     context = {
#         "posts": posts,
#         "form": form,
#     }

#     return render(request, "core/index.html", context)


class PostListView(LoginRequiredMixin, View):
    """A class view that handles post rquest"""

    def get(self, request, *args, **kwargs):
        """A method that handles the get requests"""
        posts = Post.objects.all().order_by("-created_at")

        form = PostForm()

        context = {"post_list": posts, "form": form}

        return render(request, "core/index.html", context)

    def post(self, request, *args, **kwargs):
        """A method that handles the post requests"""
        posts = Post.objects.all().order_by("-created_at")

        form = PostForm(request.POST)

        if form.is_valid():
            """Checks for form validity"""
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect("core:post-detail", pk=new_post.id)

        context = {
            "post_list": posts,
            "form": form,
        }

        return render(request, "core/index.html", context)


# @login_required
# def post_detail(request, pk, status=Post.ACTIVE):
#     """Renders the post's detailed page"""
#     post = get_object_or_404(Post, id=pk)

#     # try:
#     #     user_liked = Like.objects.filter(post=post, user=request.user).exists()
#     # except Like.DoesNotExist:
#     #     user_liked = False

#     # Get the total number of likes for the post
#     # like_count = Like.objects.filter(post=post).count()

#     # Retrieve the comments for the current post
#     comments = Comment.objects.filter(post=post)

#     if request.method == "POST":
#         form = CommentForm(request.POST)

#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.user = request.user
#             comment.post = post
#             comment.save()
#             # Redirect to the same page to display the new comment
#             return redirect("core:post-detail", pk=post.id)
#     else:
#         form = CommentForm()

#     context = {
#         "post": post,
#         "form": form,
#         # "user_liked": user_liked,
#         # "like_count": like_count,
#         "comments": comments,
#     }

#     return render(request, "core/post_detail.html", context)


class PostDetailView(LoginRequiredMixin, View):
    """A class post detail class"""

    def get(self, request, pk, *args, **kwargs):
        """A get requeste method"""
        post = Post.objects.get(pk=pk)
        form = CommentForm()

        comments = Comment.objects.filter(post=post).order_by("-created_at")

        context = {
            "post": post,
            "form": form,
            "comments": comments,
        }
        return render(request, "core/post_detail.html", context)

    def post(self, request, pk, *args, **kwargs):
        """A post request method"""
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            # Redirect to the same page to display the new comment
            return redirect("core:post-detail", pk=post.id)

        comments = Comment.objects.filter(post=post).order_by("-created_at")

        context = {"post": post, "form": form, "comments": comments}

        return render(request, "core/post_detail.html", context)


# @login_required
# def like_post(request, pk, status=Post.ACTIVE):
#     """A view function that handles like/unlike actions"""

#     try:
#         post = get_object_or_404(Post, id=pk)

#         if Like.objects.filter(post=post, user=request.user).exists():
#             Like.objects.filter(post=post, user=request.user).delete()
#         else:
#             Like.objects.create(post=post, user=request.user)
#         return redirect("core:post-detail", pk=pk)
#     except (Post.DoesNotExist, Like.DoesNotExist) as e:
#         messages.error(
#             request,
#             "An error occured while processing your action, please try again later.",
#         )
#         return redirect("core:post-detail")


# @login_required
# @user_passes_test(is_post_owner)
# def post_edit(request, pk, status=Post.ACTIVE):
#     post = get_object_or_404(Post, id=pk)
#     if request.method == "POST":
#         form = PostUpdateForm(request.POST, instance=post)
#         if form.is_valid():
#             form.save()
#             return redirect("core:post-detail", pk=post.id)
#     else:
#         form = PostUpdateForm(instance=post)

#     context = {"post": post, "form": form}

#     return render(request, "core/post_edit.html", context)


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """A class that handles posts edit logic"""

    model = Post
    fields = ["content"]
    template_name = "core/post_edit.html"

    def get_success_url(self):
        pk = self.kwargs["pk"]

        return reverse_lazy("core:post-detail", kwargs={"pk": pk})

    def test_func(self):
        """Returns boolen expresion"""
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """A class that handles posts delete logic"""

    model = Post
    template_name = "core/delete_post.html"
    success_url = reverse_lazy("core:index-page")

    def test_func(self):
        """Returns boolen expresion"""
        post = self.get_object()
        return self.request.user == post.author


# @login_required
# @user_passes_test(is_post_owner)
# def comment_delete(request, post_pk, comment_pk):
#     """A function that deletes a comment"""
#     comment = Comment.objects.get(id=comment_pk)
#     post = Post.objects.get(id=post_pk)

#     if request.method == "POST":
#         comment.delete()
#         return redirect("core:post-detail", pk=post.id)

#     context = {
#         "post": post,
#         "comment": comment,
#     }
#     return render(request, "core/delete_comment.html", context)


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "core/delete_comment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = self.get_object().post
        return context

    def get_success_url(self):
        """Gets the url after successfully deleting comment"""
        return reverse_lazy("core:post-detail", kwargs={"pk": self.object.post.pk})

    def test_func(self):
        """Returns boolean expression"""
        comment = self.get_object()
        return self.request.user == comment.user


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


# @login_required
# def search(request):
#     """The search function"""
#     query = request.GET.get("query", "")

#     posts = Post.objects.filter(status=Post.ACTIVE).filter(
#         Q(title__icontains=query)
#         | Q(intro__icontains=query)
#         | Q(content__icontains=query)
#     )
#     context = {"posts": posts, "query": query}

#     return render(request, "core/search.html", context)


class AddLike(LoginRequiredMixin, View):
    """A class that Adds like"""

    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)

        is_dislike = False

        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if is_dislike:
            post.dislikes.remove(request.user)

        is_like = False
        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            post.likes.add(request.user)
        elif is_like:
            post.likes.remove(request.user)

        next = request.POST.get("next", "/")
        return HttpResponseRedirect(next)


class Dislike(LoginRequiredMixin, View):
    """A class that removes likes"""

    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)

        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break
        if is_like:
            post.likes.remove(request.user)

        is_dislike = False

        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if not is_dislike:
            post.dislikes.add(request.user)

        if is_dislike:
            post.dislikes.remove(request.user)

        next = request.POST.get("next", "/")
        return HttpResponseRedirect(next)


class AddCommentLike(LoginRequiredMixin, View):
    """A class that Adds likes to the comment"""

    def post(self, request, pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)

        is_like = False
        for like in comment.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            comment.likes.add(request.user)
        elif is_like:
            comment.likes.remove(request.user)

        next = request.POST.get("next", "/")
        return HttpResponseRedirect(next)


def robots_txt(request):
    """"""
    text = [
        "User-Agent: *",
        "Disallow: /admin/",
    ]

    return HttpResponse("\n".join(text), content_type="text/plain")
