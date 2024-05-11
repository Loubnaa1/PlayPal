from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

# Create your models here.


class ProfileModel(models.Model):
    """A class that defines and limit the extension of image upload by the user to the user profile"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
