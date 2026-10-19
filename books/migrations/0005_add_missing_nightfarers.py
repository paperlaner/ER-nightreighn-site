from django.db import migrations


def add_missing_nightfarers(apps, schema_editor):
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
            "title": "Ironeye",
            "role": "Стрелок дальнего боя",
            "description": "Точный рейндж-персонаж с акцентом на контроль дистанции и прицельный урон.",
            "year": 200,
            "pages": 55,
            "is_featured": True,
            "art": "books/official/ironeye.svg",
            "categories": ["Duelist"],
        },
        {
            "title": "Raider",
            "role": "Силовой боец",
            "description": "Тяжелый фронтлайн-боец с высоким давлением в ближнем бою и мощными разменами.",
            "year": 260,
            "pages": 55,
            "is_featured": True,
            "art": "books/official/raider.svg",
            "categories": ["Frontline"],
        },
        {
            "title": "Executor",
            "role": "Крит-дуэлянт",
            "description": "Мобильный исполнитель с высоким потенциалом критического урона и точечных входов.",
            "year": 220,
            "pages": 55,
            "is_featured": True,
            "art": "books/official/executor.svg",
            "categories": ["Duelist"],
        },
        {
            "title": "Revenant",
            "role": "Колдун-призыватель",
            "description": "Кастер с сильной поддержкой через призывы, контроль пространства и магический темп.",
            "year": 200,
            "pages": 80,
            "is_featured": True,
            "art": "books/official/revenant.svg",
            "categories": ["Support", "Arcane"],
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
        ("books", "0004_book_official_art"),
    ]

    operations = [
        migrations.RunPython(add_missing_nightfarers, migrations.RunPython.noop),
    ]
