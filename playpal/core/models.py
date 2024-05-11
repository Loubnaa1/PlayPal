from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


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


# Create your models here.
class Post(models.Model):
    ACTIVE = "active"
    DRAFT = "draft"

    CHOICES_STATUS = [(ACTIVE, "Active"), (DRAFT, "Draft")]

    # category = models.ForeignKey(
    #     Category, related_name="posts", on_delete=models.CASCADE, null=True, blank=True
    # )
    slug = models.SlugField(unique=True, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=CHOICES_STATUS, default=ACTIVE)
    image = models.ImageField(upload_to="uploads/", blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ("-created_at",)

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

    @property
    def excerpt(self):
        """Returns the first 50 characters of the content"""
        return self.content[:50]


# class Post(models.Model):
#     ACTIVE = "active"
#     DRAFT = "draft"

#     CHOICES_STATUS = [(ACTIVE, "Active"), (DRAFT, "Draft")]

#     # category = models.ForeignKey(
#     #     Category, related_name="posts", on_delete=models.CASCADE, null=True, blank=True
#     # )
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=10, choices=CHOICES_STATUS, default=ACTIVE)
#     image = models.ImageField(upload_to="uploads/", blank=True, null=True)
#     author = models.ForeignKey(User, on_delete=models.CASCADE)

#     class Meta:
#         ordering = ("-created_at",)

#     def __str__(self):
#         return f"Post {self.id}"

#     def get_absolute_url(self):
#         """Gets the absolute url"""
#         return f"/{self.id}/"

#     @property
#     def excerpt(self):
#         """Returns the first 50 characters of the content"""
#         return self.content[:50]

class Comment(models.Model):
    """A comment class"""

    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class Follow(models.Model):
    pass
