from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap

from .sitemaps import CategorySiteMap, PostSiteMap
from core.views import robots_txt

sitemaps = {"category": CategorySiteMap, "post": PostSiteMap}

context = {"sitemaps": sitemaps}

urlpatterns = [
    path("sitemap.xml", sitemap, context),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("admin/", admin.site.urls),
    path("", include("landing.urls")),
    path("", include("users.urls")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
