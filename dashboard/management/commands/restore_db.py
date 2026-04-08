import json
import os
import subprocess

from django.conf import settings
from django.core import serializers
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Bazani backupdan qaytarish"

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str, help="Backup fayl nomi (backups/ papkada)")
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Tasdiqlash (bu amalni qaytarib bo'lmaydi!)",
        )

    def handle(self, *args, **options):
        backup_dir = os.path.join(settings.BASE_DIR, "backups")
        filename = options["filename"]
        filepath = os.path.join(backup_dir, filename)

        if not os.path.exists(filepath):
            self.stdout.write(self.style.ERROR(f"Fayl topilmadi: {filepath}"))
            self.stdout.write("\nMavjud backuplar:")
            if os.path.exists(backup_dir):
                for backup_name in sorted(os.listdir(backup_dir)):
                    size = os.path.getsize(os.path.join(backup_dir, backup_name)) / 1024
                    self.stdout.write(f"  {backup_name} ({size:.1f} KB)")
            return

        if not options["confirm"]:
            self.stdout.write(
                self.style.WARNING(
                    f"\nDIQQAT: Bu amal hozirgi barcha ma'lumotlarni O'CHIRADI!\n"
                    f"Fayl: {filename}\n\n"
                    f"Tasdiqlash uchun qayta ishga tushiring:\n"
                    f"  python manage.py restore_db {filename} --confirm\n"
                )
            )
            return

        if filename.endswith(".sql"):
            db = settings.DATABASES["default"]
            env = os.environ.copy()
            env["PGPASSWORD"] = db["PASSWORD"]

            self.stdout.write("SQL dan qaytarilmoqda...")

            cmd = [
                "psql",
                "-U",
                db["USER"],
                "-h",
                db.get("HOST", "localhost"),
                "-p",
                str(db.get("PORT", "5432")),
                "-d",
                db["NAME"],
                "-f",
                filepath,
                "--quiet",
            ]

            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS("SQL backup dan qaytarildi!"))
            else:
                self.stdout.write(self.style.ERROR(f"Xato: {result.stderr}"))

        elif filename.endswith(".json"):
            self.stdout.write("JSON dan qaytarilmoqda...")

            with open(filepath, "r", encoding="utf-8") as json_stream:
                data = json.load(json_stream)

            model_order = [
                "users",
                "seller_profiles",
                "categories",
                "products",
                "product_images",
                "orders",
                "order_items",
                "site_settings",
                "audit_logs",
                "banners",
                "pages",
                "news",
                "messages",
            ]

            for key in model_order:
                if key in data and data[key]:
                    try:
                        objects = serializers.deserialize("json", json.dumps(data[key]))
                        count = 0
                        for obj in objects:
                            obj.save()
                            count += 1
                        self.stdout.write(f"  {key}: {count} ta yozuv qaytarildi")
                    except Exception as error:
                        self.stdout.write(self.style.WARNING(f"  {key}: xato - {error}"))

            self.stdout.write(self.style.SUCCESS("JSON backup dan qaytarildi!"))

        else:
            self.stdout.write(self.style.ERROR("Faqat .sql yoki .json fayllar qo'llab-quvvatlanadi"))
