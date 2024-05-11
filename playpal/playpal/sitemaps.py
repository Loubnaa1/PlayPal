from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from core.models import Post, Category


class CategorySiteMap(Sitemap):
    """A site map structure for category"""

    def items(self):
        """Returns all objects in category class"""
        return Category.objects.all()


class PostSiteMap(Sitemap):
    """A site map structure for posts"""

    def items(self):
        """Returns all active posts in Post class"""
        return Post.objects.filter(status=Post.ACTIVE)

    def last_mod(self, obj):
        """Returns the last object modification date"""
        return obj.created_at
