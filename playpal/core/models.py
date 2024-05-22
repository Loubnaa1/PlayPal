from datetime import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


# Create your models here.
class Post(models.Model):
    ACTIVE = "active"
    DRAFT = "draft"

    CHOICES_STATUS = [(ACTIVE, "Active"), (DRAFT, "Draft")]

    shared_content = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    content = models.TextField(max_length=400)
    created_at = models.DateTimeField(auto_now_add=True)
    shared_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=CHOICES_STATUS, default=ACTIVE)
    image = models.ImageField(upload_to="uploads/post_photos", blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="+", blank=True, null=True
    )
    likes = models.ManyToManyField(User, blank=True, related_name="likes")
    dislikes = models.ManyToManyField(User, blank=True, related_name="dislikes")
    tags = models.ManyToManyField("Tag", blank=True)

    def create_tags(self):
        for word in self.content.split():
            if word[0] == "#":
                tag = Tag.objects.filter(name=word[1:]).first()
                if tag:
                    self.tags.add(tag.pk)
                else:
                    tag = Tag(name=word[1:])
                    tag.save()
                    self.tags.add(tag.pk)
                self.save()

    class Meta:
        ordering = ("-created_at", "-shared_at")

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
    tags = models.ManyToManyField("Tag", blank=True)

    def create_tags(self):
        for word in self.content.split():
            if word[0] == "#":
                tag = Tag.objects.get(name=word[1:])
                if tag:
                    self.tags.add(tag.pk)
                else:
                    tag = Tag(name=word[1:])
                    tag.save()
                    self.tags.add(tag.pk)
                self.save()

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


class ThreadModel(models.Model):
    """A thread class that handles the thread logic"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)


class MessageModel(models.Model):
    """A message module that handles the message logic"""

    thread = models.ForeignKey(
        "ThreadModel", related_name="+", on_delete=models.CASCADE, blank=True, null=True
    )
    sender_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    receiver_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    content = models.CharField(max_length=1000)
    image = models.ImageField(upload_to="uploads/message_photos", blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


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
        4 -> Dm
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
    # Thread Notification
    thread = models.ForeignKey(
        "ThreadModel", on_delete=models.CASCADE, related_name="+", blank=True, null=True
    )
    date = models.DateTimeField(auto_now_add=True)

    # A boolean value to check if a user has seen a notification or not
    user_has_seen = models.BooleanField(default=False)


class Tag(models.Model):
    name = models.CharField(max_length=255)
