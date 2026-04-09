import json
import os
import platform
import subprocess
from datetime import datetime

from django.conf import settings
from django.core import serializers
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Bazani backup qilish"

    def handle(self, *args, **options):
        # Backup papkasini yaratish
        backup_dir = os.path.join(settings.BASE_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Windows da pg_dump topish
        if platform.system() == "Windows":
            for ver in ["17", "16", "15", "14"]:
                pg_path = rf"C:\Program Files\PostgreSQL\{ver}\bin"
                if os.path.exists(os.path.join(pg_path, "pg_dump.exe")):
                    os.environ["PATH"] = pg_path + ";" + os.environ.get("PATH", "")
                    break

        # SQL backup
        sql_file = os.path.join(backup_dir, f"backup_{timestamp}.sql")
        db = settings.DATABASES["default"]

        try:
            env = os.environ.copy()
            env["PGPASSWORD"] = db.get("PASSWORD", "")

            cmd = [
                "pg_dump",
                "-U",
                db.get("USER", "postgres"),
                "-h",
                db.get("HOST", "localhost"),
                "-p",
                str(db.get("PORT", "5432")),
                "-d",
                db.get("NAME", "marketplace_db"),
                "-f",
                sql_file,
                "--no-owner",
                "--no-acl",
            ]

            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                size = os.path.getsize(sql_file) / 1024
                self.stdout.write(self.style.SUCCESS(f"SQL backup: {sql_file} ({size:.1f} KB)"))
            else:
                error_text = (result.stderr or result.stdout or "Noma'lum xato").strip()[:200]
                self.stdout.write(self.style.WARNING(f"SQL xato: {error_text}"))
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING("pg_dump topilmadi — faqat JSON backup"))

        # JSON backup
        json_file = os.path.join(backup_dir, f"backup_{timestamp}.json")
        data = {"timestamp": timestamp}

        models_to_backup = [
            ("accounts", "CustomUser"),
            ("accounts", "SellerProfile"),
            ("products", "Category"),
            ("products", "Product"),
            ("products", "ProductImage"),
            ("orders", "Order"),
            ("orders", "OrderItem"),
        ]

        optional_models = [
            ("superadmin", "SiteSettings"),
            ("superadmin", "AuditLog"),
            ("frontend", "Banner"),
            ("frontend", "Page"),
            ("frontend", "News"),
            ("frontend", "NewsCategory"),
            ("frontend", "ContactMessage"),
            ("frontend", "MenuItem"),
            ("dashboard", "SiteVisit"),
            ("dashboard", "SearchQuery"),
        ]

        for app, model_name in models_to_backup + optional_models:
            try:
                from django.apps import apps

                model = apps.get_model(app, model_name)
                key = f"{app}_{model_name}".lower()
                data[key] = json.loads(serializers.serialize("json", model.objects.all()))
            except Exception:
                pass

        with open(json_file, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, default=str, ensure_ascii=False)

        size = os.path.getsize(json_file) / 1024
        self.stdout.write(self.style.SUCCESS(f"JSON backup: {json_file} ({size:.1f} KB)"))
        self.stdout.write(self.style.SUCCESS("Backup tayyor!"))
