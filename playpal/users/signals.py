from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProfileModel


@receiver(post_save, sender=User)
def create_profile(sender, created, instance, *args, **kwargs):
    """A function that automatically creates a profile for a newly registered user."""
    if created:
        ProfileModel.objects.create(user=instance)
