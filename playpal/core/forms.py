from django import forms
from .models import Comment, Post, MessageModel


class PostForm(forms.ModelForm):
    """Handles the post form"""

    content = forms.CharField(
        label="",
        widget=forms.Textarea(
            attrs={
                "rows": "3",
                "placeholder": "Share your gaming experiences with the community..",
            }
        ),
    )

    image = forms.ImageField(required=False)

    class Meta:
        model = Post
        fields = ["content", "image"]


class CommentForm(forms.ModelForm):
    """A comment form for making comments"""

    content = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "rows": 2,
                "placeholder": "Add your thoughts...",
            }
        ),
    )

    class Meta:
        model = Comment
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(
                attrs={"placeholder": "write your comment here...", "rows": 3}
            ),
        }
        labels = {
            "content": False,
        }


class PostUpdateForm(forms.ModelForm):
    """A post form for editing posts"""

    class Meta:
        model = Post
        fields = (
            "content",
            "status",
        )


class ThreadForm(forms.Form):
    """A thread form for making threads posts"""

    username = forms.CharField(label="", max_length=100)


class MessageForm(forms.ModelForm):
    """A message form for users input"""

    content = forms.CharField(label="", max_length=1000)
    image = forms.ImageField(required=False)

    class Meta:
        model = MessageModel
        fields = ["content", "image"]


class SharedForm(forms.Form):
    content = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={"rows": "3", "placeholder": "Say something..."}),
    )


class ExploreForm(forms.Form):
    """A form that gives the user input field to search for a post that matches the query"""

    query = forms.CharField(
        label="", widget=forms.TextInput(attrs={"placeholder": "explore tags"})
    )
