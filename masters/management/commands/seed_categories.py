from django.core.management.base import BaseCommand
from masters.models import Category


class Command(BaseCommand):
    help = "Kategoriyalarni avtomatik yaratadi (asosiy + pastki)"

    def handle(self, *args, **kwargs):
        # Asosiy kategoriyalar
        main_categories = [
            {"name": "Uy xizmatlari", "icon": "🏠", "slug": "uy-xizmatlari"},
            {"name": "Oila yordami", "icon": "👨‍👩‍👧", "slug": "oila-yordami"},
            {"name": "Transport", "icon": "🚗", "slug": "transport"},
            {"name": "Texnik xizmat", "icon": "💻", "slug": "texnik-xizmat"},
            {"name": "Go'zallik saloni", "icon": "💄", "slug": "gozallik-saloni"},
        ]

        created_main = {}
        for cat in main_categories:
            obj, created = Category.objects.get_or_create(
                slug=cat["slug"],
                defaults={"name": cat["name"], "icon": cat["icon"]}
            )
            created_main[cat["slug"]] = obj
            status = "✓ Yaratildi" if created else "— Bor edi"
            self.stdout.write(f"{status}: {obj.name}")

        # Pastki kategoriyalar
        sub_categories = [
            {"name": "Santexnik", "slug": "santexnik", "parent": "uy-xizmatlari"},
            {"name": "Elektrik", "slug": "elektrik", "parent": "uy-xizmatlari"},
            {"name": "Uy tozalash", "slug": "uy-tozalash", "parent": "uy-xizmatlari"},
            {"name": "Mebel yig'ish", "slug": "mebel-yigish", "parent": "uy-xizmatlari"},

            {"name": "Enaga", "slug": "enaga", "parent": "oila-yordami"},
            {"name": "Hamshira", "slug": "hamshira", "parent": "oila-yordami"},
            {"name": "Repetitor", "slug": "repetitor", "parent": "oila-yordami"},

            {"name": "Haydovchi", "slug": "haydovchi", "parent": "transport"},
            {"name": "Yuk tashish", "slug": "yuk-tashish", "parent": "transport"},
            {"name": "Ko'chirish xizmati", "slug": "kochirish-xizmati", "parent": "transport"},

            {"name": "Kompyuter ustasi", "slug": "kompyuter-ustasi", "parent": "texnik-xizmat"},
            {"name": "Telefon ta'mirlash", "slug": "telefon-tamirlash", "parent": "texnik-xizmat"},

            {"name": "Sartarosh", "slug": "sartarosh", "parent": "gozallik-saloni"},
            {"name": "Massajchi", "slug": "massajchi", "parent": "gozallik-saloni"},
        ]

        for sub in sub_categories:
            parent_obj = created_main.get(sub["parent"]) or Category.objects.get(slug=sub["parent"])
            obj, created = Category.objects.get_or_create(
                slug=sub["slug"],
                defaults={"name": sub["name"], "parent": parent_obj}
            )
            status = "✓ Yaratildi" if created else "— Bor edi"
            self.stdout.write(f"{status}: {obj.name} (--> {parent_obj.name})")

        self.stdout.write(self.style.SUCCESS("Barcha kategoriyalar tayyor!"))
