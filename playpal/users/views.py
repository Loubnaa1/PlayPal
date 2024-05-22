from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .form import SignUpForm, UserUpdateForm, ProfileUpdateForm
from .models import ProfileModel
from core.models import Post
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.db.models import Q, F, Value, Case, When, IntegerField
from core.models import Notification

# Create your views here.


def sign_up(request):
    """A signup form that enables users to register"""

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = SignUpForm()

    context = {
        "form": form,
    }
    return render(request, "users/sign_up.html", context)


def logout_view(request):
    """A logout function"""
    logout(request)
    return redirect("login")


# login_required()
# def user_profile(request):
#     """A function that enables user to update profile"""
#     if request.method == "POST":
#         u_form = UserUpdateForm(request.POST or None, instance=request.user)
#         p_form = ProfileUpdateForm(
#             request.POST or None,
#             request.FILES or None,
#             instance=request.user.profilemodel,
#         )

#         if u_form.is_valid() and p_form.is_valid():
#             u_form.save()
#             p_form.save()
#             return redirect("users:profile")
#     else:
#         u_form = UserUpdateForm(instance=request.user)
#         p_form = ProfileUpdateForm(instance=request.user.profilemodel)

#     context = {
#         "u_form": u_form,
#         "p_form": p_form,
#     }
#     return render(request, "users/profile.html", context)


class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = ProfileModel.objects.get(pk=pk)
        user = profile.user
        posts = Post.objects.filter(author=user).order_by("-created_at")

        # Gets the number of followers
        followers = profile.followers.all()

        if len(followers) == 0:
            is_following = False

        # Checks if a user is following a particular user or not
        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False

        number_of_followers = len(followers)

        context = {
            "user": user,
            "profile": profile,
            "posts": posts,
            "number_of_followers": number_of_followers,
            "is_following": is_following,
        }

        return render(request, "users/profile.html", context)


class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ProfileModel
    fields = [
        "name",
        "dob",
        "location",
        "language",
        "cover_image",
        "profile_image",
    ]
    template_name = "users/profile_edit.html"

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse_lazy("profile", kwargs={"pk": pk})

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user


class AddFollowers(LoginRequiredMixin, View):
    """A class that adds a followers"""

    def post(self, request, pk, *args, **kwargs):
        """A class method that makes a post request and add a follower"""
        profile = ProfileModel.objects.get(pk=pk)
        profile.followers.add(request.user)

        notification = Notification.objects.create(
            notification_type=2, from_user=request.user, to_user=profile.user
        )

        return redirect("profile", pk=profile.pk)


class RemoveFollower(LoginRequiredMixin, View):
    """A class that removes a follower"""

    def post(self, request, pk, *args, **kwargs):
        """Performs the remove followers logig"""
        profile = ProfileModel.objects.get(pk=pk)
        profile.followers.remove(request.user)

        return redirect("profile", pk=profile.pk)


class UserSearch(View):
    """A search class that performs relevant search functions"""

    def get(self, request, *args, **kwargs):
        """
        A method that performs the search query by relevance:
            If the search query matched the user's username, the relevance score is set to 3.
            If the search query matched the user's name, the relevance score is set to 2.
            If the search query matched the user's bio or location, the relevance score is set to 1.
            If the search query did not match any of the above fields, the relevance score is set to 0.

        """
        query = self.request.GET.get("query")
        profile_list = ProfileModel.objects.annotate(
            relevance_score=Case(
                When(user__username__icontains=query, then=Value(3)),
                When(name__icontains=query, then=Value(2)),
                When(bio__icontains=query, then=Value(1)),
                When(location__icontains=query, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by("-relevance_score")

        context = {"profile_list": profile_list, "query": query}

        return render(request, "users/search.html", context)


class ListFollowers(View):
    """A class that lists the number of followers"""

    def get(self, request, pk, *args, **kwargs):
        """Returns the list of number of followers"""
        profile = ProfileModel.objects.get(pk=pk)
        followers = profile.followers.all()

        context = {"profile": profile, "followers": followers}

        return render(request, "users/followers_list.html", context)
