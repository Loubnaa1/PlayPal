from typing import Any
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import ProfileModel
from django.views.generic.edit import UpdateView


class SignUpForm(UserCreationForm):
    """Provides new users with the required field to signup or register"""

    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        """A special method that get ride of form help text"""
        super(SignUpForm, self).__init__(*args, **kwargs)

        for fieldname in ["username", "email", "password1", "password2"]:
            self.fields[fieldname].help_text = None


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        """A special method that get ride of form help text"""
        super(UserUpdateForm, self).__init__(*args, **kwargs)

        for fieldname in [
            "username",
            "email",
        ]:
            self.fields[fieldname].help_text = None


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = ProfileModel
        fields = ["cover_image", "profile_image"]

