from django.db import migrations, models


def copy_cover_to_official_art(apps, schema_editor):
    Book = apps.get_model("books", "Book")
    for book in Book.objects.exclude(cover=""):
        if not book.official_art:
            book.official_art = book.cover
            book.save(update_fields=["official_art"])


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0003_author_category_and_crud"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="official_art",
            field=models.ImageField(blank=True, upload_to="books/official/", verbose_name="Официальный арт из игры"),
        ),
        migrations.RunPython(copy_cover_to_official_art, migrations.RunPython.noop),
    ]
