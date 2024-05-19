from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Post, Category, Comment, Notification
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


class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logged_in_user = request.user

        if logged_in_user.is_superuser:
            posts = Post.objects.all().order_by("-created_at")
        else:
            posts = Post.objects.filter(
                Q(author__profile__followers__in=[logged_in_user.id])
                | Q(author=logged_in_user)
            ).order_by("-created_at")

        form = PostForm()

        context = {
            "post_list": posts,
            "form": form,
        }

        return render(request, "core/index.html", context)

    def post(self, request, *args, **kwargs):
        logged_in_user = request.user
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = logged_in_user
            new_post.save()
            return redirect("core:post-detail", pk=new_post.id)

        posts = Post.objects.filter(
            Q(author__profile__followers__in=[logged_in_user.id])
            | Q(author=logged_in_user)
        ).order_by("-created_at")

        context = {
            "post_list": posts,
            "form": form,
        }

        return render(request, "core/index.html", context)


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
            # Create a notification for the post author
            if request.user != post.author:
                notification = Notification.objects.create(
                    notification_type=2,
                    from_user=request.user,
                    to_user=post.author,
                    post=post,
                )

            return redirect("core:post-detail", pk=post.id)

        comments = Comment.objects.filter(post=post).order_by("-created_at")

        context = {"post": post, "form": form, "comments": comments}
        return render(request, "core/post_detail.html", context)


class CommentReplyView(LoginRequiredMixin, View):
    """A class that handles the nested comment logic"""

    def post(self, request, post_pk, pk, *args, **kwargs):
        post = Post.objects.get(pk=post_pk)
        parent_comment = Comment.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()

        notification = Notification.objects.create(
            notification_type=2,
            from_user=request.user,
            to_user=parent_comment.post.author,
            comment=new_comment,
        )

        return redirect("core:post-detail", pk=post_pk)


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
            notification = Notification.objects.create(
                notification_type=1,
                from_user=request.user,
                to_user=post.author,
                post=post,
            )
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
            notification = Notification.objects.create(
                notification_type=2,
                from_user=request.user,
                to_user=comment.author,
                comment=comment,
            )
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


class PostNotification(View):
    def get(self, request, notification_pk, post_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        post = Post.objects.get(pk=post_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect("core:post-detail", pk=post_pk)


class FollowNotification(View):
    def get(self, request, notification_pk, profile_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        profile = ProfileModel.objects.get(pk=profile_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect("users:profile", pk=profile_pk)


class RemoveNotification(View):
    """A class that hadles notification removal"""

    def delete(self, request, notification_pk, *args, **kwargs):
        """A method that removes/ delete notification"""
        notification = Notification.objects.get(pk=notification_pk)

        notification_user_has_seen = True
        notification.save()

        return HttpResponse("Success", content_type="text/plain")
