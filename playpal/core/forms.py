from django import forms
from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Handles the post form"""

    content = forms.CharField(widget=forms.Textarea(attrs={"rows": 1}), label=False)

    class Meta:
        model = Post
        fields = ("content",)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(
                attrs={"placeholder": "write your comment here...", "rows": 1}
            ),
        }
        labels = {
            "content": False,
        }


class PostUpdateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "content",
            "status",
        )
