from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

# Create your models here.


class ProfileModel(models.Model):
    """A class that defines and limit the extension of image upload by the user to the user profile"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name="user",
        related_name="profile",
    )
    name = models.CharField(max_length=30, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, null=True)
    followers = models.ManyToManyField(User, blank=True, related_name="followers")

    cover_image = models.ImageField(
        default="cover.jpg",
        upload_to="profile",
        validators=[
            FileExtensionValidator(
                [
                    "png",
                    "jpg",
                    "jpeg",
                ]
            ),
        ],
    )

    profile_image = models.ImageField(
        default="default.jpg",
        upload_to="profile",
        validators=[
            FileExtensionValidator(
                [
                    "png",
                    "jpg",
                    "jpeg",
                ]
            ),
        ],
    )

    def __str__(self):
        return self.user.username
