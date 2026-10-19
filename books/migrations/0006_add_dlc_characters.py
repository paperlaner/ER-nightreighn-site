from django.db import migrations


def add_dlc_characters(apps, schema_editor):
    Author = apps.get_model("books", "Author")
    Category = apps.get_model("books", "Category")
    Book = apps.get_model("books", "Book")

    author, _ = Author.objects.get_or_create(
        name="FromSoftware Archive",
        defaults={"bio": "Редакционный профиль для карточек Nightreign."},
    )

    categories = {}
    for name, slug in [
        ("Frontline", "frontline"),
        ("Support", "support"),
        ("Duelist", "duelist"),
        ("Arcane", "arcane"),
    ]:
        categories[name], _ = Category.objects.get_or_create(name=name, slug=slug)

    characters = [
        {
            "title": "Scholar",
            "role": "DLC арканист",
            "description": "Новый DLC-персонаж с сильным магическим контролем и командной поддержкой.",
            "year": 205,
            "pages": 85,
            "is_featured": True,
            "art": "Новая папка/Scholar-wide.webp",
            "categories": ["Support", "Arcane"],
        },
        {
            "title": "Undertaker",
            "role": "DLC охотник",
            "description": "Новый DLC-персонаж для агрессивного прессинга и игры от статусов.",
            "year": 235,
            "pages": 65,
            "is_featured": True,
            "art": "Новая папка/Undertaker-wide.webp",
            "categories": ["Frontline", "Duelist"],
        },
    ]

    for payload in characters:
        book, created = Book.objects.get_or_create(
            title=payload["title"],
            defaults={
                "role": payload["role"],
                "author": author,
                "description": payload["description"],
                "cover": payload["art"],
                "official_art": payload["art"],
                "year": payload["year"],
                "pages": payload["pages"],
                "is_featured": payload["is_featured"],
            },
        )

        if not created:
            changed = False
            if not book.official_art:
                book.official_art = payload["art"]
                changed = True
            if not book.cover:
                book.cover = payload["art"]
                changed = True
            if changed:
                book.save(update_fields=["official_art", "cover"])

        for category_name in payload["categories"]:
            book.categories.add(categories[category_name])


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0005_add_missing_nightfarers"),
    ]

    operations = [
        migrations.RunPython(add_dlc_characters, migrations.RunPython.noop),
    ]
