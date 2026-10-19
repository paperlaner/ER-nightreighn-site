from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0006_add_dlc_characters"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Comment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nightlord_slug", models.SlugField(blank=True, max_length=160, verbose_name="Slug ?????????")),
                ("guest_name", models.CharField(blank=True, max_length=80, verbose_name="??? ?????")),
                ("body", models.TextField(max_length=1200, verbose_name="???????????")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="??????")),
                (
                    "book",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="books.book",
                        verbose_name="????????",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="comments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="????????????",
                    ),
                ),
            ],
            options={
                "verbose_name": "???????????",
                "verbose_name_plural": "???????????",
                "ordering": ["-created_at"],
            },
        ),
    ]
