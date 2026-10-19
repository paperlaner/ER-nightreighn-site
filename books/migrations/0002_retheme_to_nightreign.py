from django.db import migrations


def seed_nightreign(apps, schema_editor):
    Book = apps.get_model("books", "Book")
    Book.objects.all().delete()
    Book.objects.bulk_create(
        [
            Book(
                title="Wylder",
                author="Боец-универсал",
                description="Сбалансированный Nightfarer для агрессивного старта, хорошего контроля дистанции и гибких билдов.",
                cover="books/wylder.svg",
                year=240,
                pages=65,
                is_featured=True,
            ),
            Book(
                title="Guardian",
                author="Танк-защитник",
                description="Самый устойчивый персонаж в группе. Берет на себя давление, удерживает врагов и дает команде пространство.",
                cover="books/guardian.svg",
                year=280,
                pages=55,
                is_featured=True,
            ),
            Book(
                title="Duchess",
                author="Ловкий дуэлянт",
                description="Высокая мобильность, сильный burst и комфортная игра от уклонений. Подходит для точного и быстрого темпа.",
                cover="books/duchess.svg",
                year=220,
                pages=75,
                is_featured=True,
            ),
            Book(
                title="Recluse",
                author="Маг поддержки",
                description="Персонаж с сильным магическим масштабированием. Хорошо раскрывается в контроле боя и командной поддержке.",
                cover="books/recluse.svg",
                year=200,
                pages=80,
                is_featured=False,
            ),
        ]
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_nightreign, noop),
    ]
