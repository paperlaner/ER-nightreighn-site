from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class Author(models.Model):
    name = models.CharField("Name", max_length=120, unique=True)
    bio = models.TextField("Description", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField("Name", max_length=80, unique=True)
    slug = models.SlugField("Slug", max_length=80, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    title = models.CharField("Title", max_length=160)
    role = models.CharField("Role", max_length=120, blank=True)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="books",
        verbose_name="Author",
    )
    categories = models.ManyToManyField(
        Category,
        related_name="books",
        verbose_name="Categories",
        blank=True,
    )
    description = models.TextField("Description")
    cover = models.ImageField("Cover", upload_to="books/")
    official_art = models.ImageField("Official art", upload_to="books/official/", blank=True)
    year = models.PositiveIntegerField("Year")
    pages = models.PositiveIntegerField("Pages")
    is_featured = models.BooleanField("Featured", default=False)

    class Meta:
        ordering = ["title"]
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("books:book_detail", args=[self.pk])


class Comment(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Book",
        null=True,
        blank=True,
    )
    nightlord_slug = models.SlugField("Nightlord slug", max_length=160, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="comments",
        verbose_name="User",
        null=True,
        blank=True,
    )
    guest_name = models.CharField("Guest name", max_length=80, blank=True)
    body = models.TextField("Comment", max_length=1200)
    created_at = models.DateTimeField("Created", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self) -> str:
        return f"Comment #{self.pk}"

    @property
    def author_name(self) -> str:
        if self.user_id:
            return self.user.get_username()
        if self.guest_name:
            return self.guest_name
        return "Anonymous"

    def clean(self) -> None:
        super().clean()
        has_book = bool(self.book_id)
        has_nightlord = bool(self.nightlord_slug)
        if has_book and has_nightlord:
            raise ValidationError("Comment cannot be attached to both a character and a nightlord.")
        if self.pk and not (has_book or has_nightlord):
            raise ValidationError("Comment must be attached to a character or a nightlord.")



class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_books",
        verbose_name="User",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Book",
    )
    created_at = models.DateTimeField("Created", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
        constraints = [
            models.UniqueConstraint(fields=["user", "book"], name="unique_user_book_favorite"),
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.book}"
