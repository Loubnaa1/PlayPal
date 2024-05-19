from django import forms
from .models import Comment, Post


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
        fields = ['content', 'image']


class CommentForm(forms.ModelForm):
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
    class Meta:
        model = Post
        fields = (
            "content",
            "status",
        )
