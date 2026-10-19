from django import forms

from .models import Author, Book, Comment


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title",
            "role",
            "author",
            "categories",
            "description",
            "cover",
            "official_art",
            "year",
            "pages",
            "is_featured",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "categories": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].label = "Имя персонажа"
        self.fields["role"].label = "Роль"
        self.fields["author"].label = "Автор записи"
        self.fields["categories"].label = "Категории"
        self.fields["description"].label = "Описание билда"
        self.fields["cover"].label = "Портрет"
        self.fields["official_art"].label = "Официальный арт из игры"
        self.fields["year"].label = "HP"
        self.fields["pages"].label = "FP"
        self.fields["is_featured"].label = "Показывать на главной"


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["guest_name", "body"]
        widgets = {
            "guest_name": forms.TextInput(attrs={"placeholder": "Имя для комментария"}),
            "body": forms.Textarea(attrs={"rows": 4, "placeholder": "Напишите комментарий"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["guest_name"].required = False
        self.fields["guest_name"].label = "Имя"
        self.fields["body"].label = "Комментарий"
        if user and user.is_authenticated:
            self.fields.pop("guest_name")

    def save_for_target(self, *, user, book=None, nightlord_slug=""):
        comment = self.save(commit=False)
        comment.user = user if user and user.is_authenticated else None
        comment.book = book
        comment.nightlord_slug = nightlord_slug
        if comment.user_id:
            comment.guest_name = ""
        elif not comment.guest_name:
            comment.guest_name = "Аноним"
        comment.full_clean()
        comment.save()
        return comment


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ["name", "bio"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }
