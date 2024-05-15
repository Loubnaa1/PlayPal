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

# Create your views here.


def sign_up(request):
    """A signup form that enables users to register"""

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:login")
    else:
        form = SignUpForm()

    context = {
        "form": form,
    }
    return render(request, "users/sign_up.html", context)


def logout_view(request):
    """A logout function"""
    logout(request)
    return redirect("users:login")


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
        return reverse_lazy("users:profile", kwargs={"pk": pk})

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user


class AddFollowers(LoginRequiredMixin, View):
    """A class that adds a followers"""

    def post(self, request, pk, *args, **kwargs):
        """A class method that makes a post request and add a follower"""
        profile = ProfileModel.objects.get(pk=pk)
        profile.followers.add(request.user)

        return redirect("users:profile", pk=profile.pk)


class RemoveFollower(LoginRequiredMixin, View):
    """A class that removes a follower"""

    def post(self, request, pk, *args, **kwargs):
        """Performs the remove followers logig"""
        profile = ProfileModel.objects.get(pk=pk)
        profile.followers.remove(request.user)

        return redirect("users:profile", pk=profile.pk)
