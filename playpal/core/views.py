from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Post, Category, Comment, Notification, MessageModel
from .forms import CommentForm, PostForm, ThreadForm, MessageForm, SharedForm
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
from .models import ThreadModel, Tag
from django.utils import timezone
import requests
from django.conf import settings
from django.core.cache import cache
from .forms import ExploreForm


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
        shared_form = SharedForm()

        context = {"post_list": posts, "form": form, "shared_form": shared_form}

        return render(request, "core/index.html", context)

    def post(self, request, *args, **kwargs):
        logged_in_user = request.user
        form = PostForm(request.POST, request.FILES)
        shared_form = SharedForm()

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = logged_in_user
            new_post.save()
            new_post.create_tags()
            return redirect("core:post-detail", pk=new_post.id)

        posts = Post.objects.filter(
            Q(author__profile__followers__in=[logged_in_user.id])
            | Q(author=logged_in_user)
        ).order_by("-created_at")

        context = {"post_list": posts, "form": form, "shared_form": shared_form}

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
            comment.create_tags()
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

        return redirect("profile", pk=profile_pk)


class ThreadNotification(View):
    """A class that handles thread notification logic"""

    def get(self, request, notification_pk, object_pk, *args, **kwargs):
        """Gets the notification object and mark it as seen and redirect to thread"""
        notification = Notification.objects.get(pk=notification_pk)
        thread = ThreadModel.objects.get(pk=object_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect("core:thread", pk=object_pk)


class RemoveNotification(View):
    """A class that hadles notification removal"""

    def delete(self, request, notification_pk, *args, **kwargs):
        """A method that removes/ delete notification"""
        notification = Notification.objects.get(pk=notification_pk)

        notification_user_has_seen = True
        notification.save()

        return HttpResponse("Success", content_type="text/plain")


class ListThread(View):
    """A class that handles the thred view"""

    def get(self, request, *args, **kwargs):
        """A method that gets the lists of thread"""
        threads = ThreadModel.objects.filter(
            Q(user=request.user) | Q(receiver=request.user)
        )

        context = {"threads": threads}
        return render(request, "core/inbox.html", context)


class CreateThread(View):
    """A class that handles create and sends methods for creating a thread"""

    def get(self, request, *args, **kwargs):
        """handles the get request logic"""
        form = ThreadForm()

        context = {"form": form}

        return render(request, "core/create_thread.html", context)

    def post(self, request, *args, **kwargs):
        """This handles the logic of creating a new thread"""
        form = ThreadForm(request.POST)

        username = request.POST.get("username")
        try:
            receiver = User.objects.get(username=username)
            # Does the thread exist?
            if ThreadModel.objects.filter(
                user=request.user, receiver=receiver
            ).exists():
                thread = ThreadModel.objects.filter(
                    user=request.user, receiver=receiver
                )[0]
                return redirect("core:thread", pk=thread.pk)
            elif ThreadModel.objects.filter(
                user=receiver, receiver=request.user
            ).exists():
                thread = ThreadModel.objects.filter(
                    user=receiver, receiver=request.user
                )[0]
                return redirect("core:thread", pk=thread.pk)
            # if not
            if form.is_valid():
                thread = ThreadModel(user=request.user, receiver=receiver)
                thread.save()
                return redirect("core:thread", pk=thread.pk)

        except:
            messages.error(
                request, "Invalid Username, please try again with a valid username"
            )
            # if user does not exists
            return redirect("core:create-thread")


class ThreadView(View):
    """A thread view class"""

    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        thread = ThreadModel.objects.get(pk=pk)
        message_list = MessageModel.objects.filter(thread__pk__contains=pk)
        context = {"thread": thread, "form": form, "message_list": message_list}

        return render(request, "core/thread.html", context)


class CreateMessage(View):
    """A seperate view that redirects to whereever view one wish to go to"""

    def post(self, request, pk, *args, **kwargs):
        form = MessageForm(request.POST, request.FILES)
        thread = ThreadModel.objects.get(pk=pk)

        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver

        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender_user = request.user
            message.receiver_user = receiver
            message.save()

        notfication = Notification.objects.create(
            notification_type=4, from_user=request.user, to_user=receiver, thread=thread
        )

        return redirect("core:thread", pk=pk)


class SharedPost(View):
    """A class that handles the shared post logic"""

    def get(self, request, pk, *args, **kwargs):
        """Gets the original post to be shared"""
        original_post = Post.objects.get(pk=pk)
        form = SharedForm()
        context = {
            "original_post": original_post,
            "shared_form": form,
        }
        return render(request, "core/index.html", context)

    def post(self, request, pk, *args, **kwargs):
        """Handles the sharing of a post"""
        original_post = Post.objects.get(pk=pk)
        form = SharedForm(request.POST)

        if form.is_valid():
            new_post = Post(
                shared_content=form.cleaned_data["content"],
                content=original_post.content,
                author=original_post.author,
                created_at=original_post.created_at,
                shared_user=request.user,
                shared_at=timezone.now(),
            )
            new_post.save()
            return redirect("core:index-page")

        context = {
            "original_post": original_post,
            "shared_form": form,
        }
        return render(request, "core/index.html", context)


class TrendingGamesView(View):
    def get(self, request, *args, **kwargs):
        """Make the API request to Reddit"""

        trending_games = cache.get("trending_games")
        if trending_games is not None:
            return render(
                request, "core/games.html", {"trending_games": trending_games}
            )

        # fectch data from Reddit API

        try:
            response = requests.get("https://www.reddit.com/r/gaming/new.json?limit=10")
            response.raise_for_status()
            data = response.json()
            trending_games = [
                "post"["data"]["title"] for post in data["data"]["children"]
            ]

            # Cach the trending games data for a certain duration
            cache.set("treanding_games", trending_games, timeout=settings.CACHE_TIMEOUT)

            return render(
                request, "core/games.html", {"trending_games": trending_games}
            )
        except request.execptions.RequestException as e:
            return render(request, "core/games.html", {"error": str(e)})

        # Process the response data
        data = response.json()
        trending_games = [post["data"]["title"] for post in data["data"]["children"]]

        # Pass the trending games to the template
        context = {"trending_games": trending_games}
        return render(request, "core/games.html", context)


class Explore(View):
    """A class that performs the explore logic"""

    def get(self, request, *args, **kwargs):
        explore_form = ExploreForm()

        query = self.request.GET.get("query")
        tag = Tag.objects.filter(name=query).first()

        if tag:
            posts = Post.objects.filter(tags__in=[tag])
        else:
            posts = Post.objects.all()

        context = {
            "tag": tag,
            "posts": posts,
            "explore_form": explore_form,
        }

        return render(request, "core/explore.html", context)

    def post(self, request, *args, **kwargs):
        explore_form = ExploreForm(request.POST)
        if explore_form.is_valid():
            query = explore_form.cleaned_data["query"]
            tag = Tag.objects.filter(name=query).first()

            posts = None
            if tag:
                posts = Post.objects.filter(tags__in=[tag])
            if posts:
                context = {"tag": tag, "posts": posts}
            else:
                context = {
                    "tag": tag,
                }
            return HttpResponseRedirect(f"/core/explore?query={query}")
        return HttpResponseRedirect("/core/explore")
