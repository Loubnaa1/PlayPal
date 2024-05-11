from django.contrib import admin
from .models import Post, Category, Comment


class CommentInline(admin.TabularInline):
    """Shows items in a tabula form"""

    model = Comment
    row_id_fields = ["post"]


class PostAdmin(admin.ModelAdmin):
    """A Post class for the admin with public attributes that defines the search functionality in the admin pannel"""

    search_fields = ["content"]
    list_display = ["created_at", "status"]
    list_filter = ["created_at", "status"]
    inlines = [CommentInline]


class CategoryAdmin(admin.ModelAdmin):
    """A Category class for the admin with public attributes that defines the search functionality in he admin pannel"""

    search_fields = ["title"]
    list_display = ["title"]
    prepopulated_fields = {
        "slug": [
            "title",
        ]
    }


class CommentAdmin(admin.ModelAdmin):
    """A Comment class for the admin with public attributes that defines the search functionality in he admin pannel"""

    # search_fields = ["title"]
    list_display = ["name", "post", "created_at"]


# Register your models here.

admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)