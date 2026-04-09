import json
import os
import platform
import subprocess
from datetime import datetime

from django.conf import settings
from django.core import serializers
from django.core.management.base import BaseCommand

from accounts.models import CustomUser, SellerProfile
from orders.models import Order, OrderItem
from products.models import Category, Product, ProductImage


class Command(BaseCommand):
    help = "Bazani backup qilish (SQL + JSON)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--format",
            type=str,
            default="both",
            choices=["sql", "json", "both"],
            help="Backup formati: sql, json, yoki both",
        )

    def handle(self, *args, **options):
        # Windows da PostgreSQL bin papkasini avtomatik topish
        if platform.system() == "Windows":
            pg_paths = [
                r"C:\Program Files\PostgreSQL\16\bin",
                r"C:\Program Files\PostgreSQL\17\bin",
                r"C:\Program Files\PostgreSQL\15\bin",
                r"C:\Program Files (x86)\PostgreSQL\16\bin",
            ]
            for pg_path in pg_paths:
                if os.path.exists(os.path.join(pg_path, "pg_dump.exe")):
                    os.environ["PATH"] = pg_path + ";" + os.environ.get("PATH", "")
                    break

        backup_dir = os.path.join(settings.BASE_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fmt = options["format"]

        if fmt in ["sql", "both"]:
            sql_file = os.path.join(backup_dir, f"backup_{timestamp}.sql")
            db = settings.DATABASES["default"]

            try:
                env = os.environ.copy()
                env["PGPASSWORD"] = db["PASSWORD"]

                cmd = [
                    "pg_dump",
                    "-U",
                    db["USER"],
                    "-h",
                    db.get("HOST", "localhost"),
                    "-p",
                    str(db.get("PORT", "5432")),
                    "-d",
                    db["NAME"],
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
                    self.stdout.write(self.style.ERROR(f"SQL xato: {result.stderr}"))

            except FileNotFoundError:
                self.stdout.write(
                    self.style.WARNING(
                        "pg_dump topilmadi. PATH ga qo'shing:\n"
                        '$env:Path += ";C:\\Program Files\\PostgreSQL\\16\\bin"'
                    )
                )

        if fmt in ["json", "both"]:
            json_file = os.path.join(backup_dir, f"backup_{timestamp}.json")

            data = {
                "timestamp": timestamp,
                "users": json.loads(serializers.serialize("json", CustomUser.objects.all())),
                "seller_profiles": json.loads(serializers.serialize("json", SellerProfile.objects.all())),
                "categories": json.loads(serializers.serialize("json", Category.objects.all())),
                "products": json.loads(serializers.serialize("json", Product.objects.all())),
                "product_images": json.loads(serializers.serialize("json", ProductImage.objects.all())),
                "orders": json.loads(serializers.serialize("json", Order.objects.all())),
                "order_items": json.loads(serializers.serialize("json", OrderItem.objects.all())),
            }

            try:
                from superadmin.models import AuditLog, SiteSettings

                data["site_settings"] = json.loads(serializers.serialize("json", SiteSettings.objects.all()))
                data["audit_logs"] = json.loads(serializers.serialize("json", AuditLog.objects.all()[:500]))
            except Exception:
                pass

            try:
                from frontend.models import Banner, ContactMessage, News, Page

                data["banners"] = json.loads(serializers.serialize("json", Banner.objects.all()))
                data["pages"] = json.loads(serializers.serialize("json", Page.objects.all()))
                data["news"] = json.loads(serializers.serialize("json", News.objects.all()))
                data["messages"] = json.loads(serializers.serialize("json", ContactMessage.objects.all()))
            except Exception:
                pass

            with open(json_file, "w", encoding="utf-8") as json_stream:
                json.dump(data, json_stream, indent=2, default=str, ensure_ascii=False)

            size = os.path.getsize(json_file) / 1024
            self.stdout.write(self.style.SUCCESS(f"JSON backup: {json_file} ({size:.1f} KB)"))

        self.clean_old_backups(backup_dir, days=30)
        self.stdout.write(self.style.SUCCESS("Backup tayyor!"))

    def clean_old_backups(self, backup_dir, days=30):
        import time

        now = time.time()
        count = 0
        for file_name in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, file_name)
            if os.path.isfile(file_path):
                age_days = (now - os.path.getmtime(file_path)) / 86400
                if age_days > days:
                    os.remove(file_path)
                    count += 1
        if count:
            self.stdout.write(f"{count} ta eski backup o'chirildi")
