from django.contrib import admin

from .models import Author, Book, Category, Comment, Favorite

admin.site.site_header = "Nightreign Admin"
admin.site.site_title = "Nightreign Admin"
admin.site.index_title = "?????????? ???????????, ??????? ? ?????????"


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "role", "author", "year", "pages", "is_featured")
    list_filter = ("is_featured", "categories", "author")
    search_fields = ("title", "role", "author__name")
    filter_horizontal = ("categories",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author_name", "book", "nightlord_slug", "created_at")
    list_filter = ("created_at",)
    search_fields = ("guest_name", "body", "nightlord_slug", "user__username", "book__title")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "book__title")
