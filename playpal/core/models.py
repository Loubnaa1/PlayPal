from datetime import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


# Create your models here.
class Post(models.Model):
    ACTIVE = "active"
    DRAFT = "draft"

    CHOICES_STATUS = [(ACTIVE, "Active"), (DRAFT, "Draft")]

    slug = models.SlugField(unique=True, blank=True, null=True)
    content = models.TextField(max_length=400)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=CHOICES_STATUS, default=ACTIVE)
    image = models.ImageField(upload_to="uploads/post_photos", blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, blank=True, related_name="likes")
    dislikes = models.ManyToManyField(User, blank=True, related_name="dislikes")

    class Meta:
        ordering = ("-created_at",)

    def comment_count(self):
        """Counts the comment of a post"""
        return self.comments.all().count()

    def get_like_count(self):
        """A cound method that returns the number of likes for the post"""
        return self.likes.count()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.content[:50])
            self.slug = base_slug
            count = 1

            while Post.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{base_slug}-{count}"
                count += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        """Gets the absolute url"""
        return f"/{self.slug}/"



class Comment(models.Model):
    """A comment class"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    content = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name="comment_likes")

    # forein key to the parent class of the comment attribute
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="+"
    )

    @property
    def children(self):
        return Comment.objects.filter(parent=self).order_by("-created_at").all()

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.content


class Category(models.Model):
    """A category class that inherits from models module"""

    title = models.CharField(max_length=255)
    slug = models.SlugField()

    class Meta:
        ordering = ("title",)
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Gets the absolute url"""
        return "/%s/" % self.slug


class Notification(models.Model):
    """
    A class that handles notification logic
    Relevance/Meaning:
        1 -> Like
        2 -> Comment
        3 -> Following
    """

    notification_type = models.IntegerField()

    # The user to recieve notification 
    to_user = models.ForeignKey(
        User, related_name="notification_to", on_delete=models.CASCADE, null=True
    )

    # the user to make notification
    from_user = models.ForeignKey(
        User, related_name="notification_from", on_delete=models.CASCADE, null=True
    )

    # a Post notifcation
    post = models.ForeignKey(
        "Post", on_delete=models.CASCADE, related_name="+", blank=True, null=True
    )

    # A comment notification
    comment = models.ForeignKey(
        "Comment", on_delete=models.CASCADE, related_name="+", blank=True, null=True
    )
    date = models.DateTimeField(auto_now_add=True)
    
    # A boolean value to check if a user has seen a notification or not
    user_has_seen = models.BooleanField(default=False)
