from django.db import migrations, models
import django.db.models.deletion


def create_seed_author(apps, schema_editor):
    Author = apps.get_model("books", "Author")
    Author.objects.get_or_create(
        name="FromSoftware Archive",
        defaults={"bio": "Редакционный профиль для карточек Nightreign."},
    )


def forwards(apps, schema_editor):
    Author = apps.get_model("books", "Author")
    Category = apps.get_model("books", "Category")
    Book = apps.get_model("books", "Book")

    archive_author = Author.objects.get(name="FromSoftware Archive")

    category_map = {}
    for name, slug in [
        ("Frontline", "frontline"),
        ("Support", "support"),
        ("Duelist", "duelist"),
        ("Arcane", "arcane"),
    ]:
        category_map[name], _ = Category.objects.get_or_create(name=name, slug=slug)

    for book in Book.objects.all():
        book.author = archive_author
        book.save(update_fields=["author"])

        if book.title in {"Wylder", "Guardian"}:
            book.categories.add(category_map["Frontline"])
        if book.title == "Duchess":
            book.categories.add(category_map["Duelist"])
        if book.title == "Recluse":
            book.categories.add(category_map["Support"], category_map["Arcane"])


def backwards(apps, schema_editor):
    Book = apps.get_model("books", "Book")
    for book in Book.objects.all():
        book.role = f"{book.role} ({book.author.name})".strip()
        book.save(update_fields=["role"])


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0002_retheme_to_nightreign"),
    ]

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True, verbose_name="Имя")),
                ("bio", models.TextField(blank=True, verbose_name="Описание")),
            ],
            options={
                "verbose_name": "Автор",
                "verbose_name_plural": "Авторы",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True, verbose_name="Название")),
                ("slug", models.SlugField(max_length=80, unique=True, verbose_name="Slug")),
            ],
            options={
                "verbose_name": "Категория",
                "verbose_name_plural": "Категории",
                "ordering": ["name"],
            },
        ),
        migrations.RunPython(create_seed_author, migrations.RunPython.noop),
        migrations.RenameField(
            model_name="book",
            old_name="author",
            new_name="role",
        ),
        migrations.AddField(
            model_name="book",
            name="author",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="books",
                to="books.author",
                verbose_name="Автор",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="book",
            name="categories",
            field=models.ManyToManyField(blank=True, related_name="books", to="books.category", verbose_name="Категории"),
        ),
        migrations.RunPython(forwards, backwards),
    ]
