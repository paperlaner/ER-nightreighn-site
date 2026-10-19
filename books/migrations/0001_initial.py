from django.db import migrations, models


def seed_books(apps, schema_editor):
    Book = apps.get_model("books", "Book")
    Book.objects.bulk_create(
        [
            Book(
                title="Дон Кихот",
                author="Мигель де Сервантес",
                description="Классический роман о рыцаре печального образа, идеалах, иронии и столкновении мечты с реальностью.",
                cover="books/classic-don-quixote.svg",
                year=1605,
                pages=863,
                is_featured=True,
            ),
            Book(
                title="Мастер и Маргарита",
                author="Михаил Булгаков",
                description="Многослойный роман с сатирой, мистикой и философскими темами о добре, свободе и ответственности.",
                cover="books/classic-master.svg",
                year=1967,
                pages=480,
                is_featured=True,
            ),
            Book(
                title="Гордость и предубеждение",
                author="Джейн Остин",
                description="Роман о характере, репутации и чувствах, построенный на тонкой социальной наблюдательности.",
                cover="books/classic-pride.svg",
                year=1813,
                pages=432,
                is_featured=False,
            ),
        ]
    )


def unseed_books(apps, schema_editor):
    Book = apps.get_model("books", "Book")
    Book.objects.filter(
        title__in=["Дон Кихот", "Мастер и Маргарита", "Гордость и предубеждение"]
    ).delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160, verbose_name="Название")),
                ("author", models.CharField(max_length=120, verbose_name="Автор")),
                ("description", models.TextField(verbose_name="Описание")),
                ("cover", models.ImageField(upload_to="books/", verbose_name="Обложка")),
                ("year", models.PositiveIntegerField(verbose_name="Год издания")),
                ("pages", models.PositiveIntegerField(verbose_name="Страниц")),
                ("is_featured", models.BooleanField(default=False, verbose_name="Рекомендуемая")),
            ],
            options={
                "verbose_name": "Книга",
                "verbose_name_plural": "Книги",
                "ordering": ["title"],
            },
        ),
        migrations.RunPython(seed_books, unseed_books),
    ]
