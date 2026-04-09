import json
import os

from django.conf import settings
from django.core import serializers
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Bazani JSON backupdan qaytarish"

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str)
        parser.add_argument("--confirm", action="store_true")

    def handle(self, *args, **options):
        backup_dir = os.path.join(settings.BASE_DIR, "backups")
        filepath = os.path.join(backup_dir, options["filename"])

        if not os.path.exists(filepath):
            self.stdout.write(self.style.ERROR(f"Fayl topilmadi: {filepath}"))
            if os.path.exists(backup_dir):
                self.stdout.write("Mavjud backuplar:")
                for file_name in sorted(os.listdir(backup_dir)):
                    self.stdout.write(f"  {file_name}")
            return

        if not options["confirm"]:
            self.stdout.write(
                self.style.WARNING(
                    "DIQQAT: Bu hozirgi ma'lumotlarni O'ZGARTIRADI!\n"
                    f"Tasdiqlash: python manage.py restore_db {options['filename']} --confirm"
                )
            )
            return

        with open(filepath, "r", encoding="utf-8") as stream:
            data = json.load(stream)

        for key, items in data.items():
            if key == "timestamp" or not isinstance(items, list):
                continue
            try:
                objects = list(serializers.deserialize("json", json.dumps(items)))
                for obj in objects:
                    obj.save()
                self.stdout.write(f"  {key}: {len(objects)} ta qaytarildi")
            except Exception as error:
                self.stdout.write(self.style.WARNING(f"  {key}: xato — {str(error)[:100]}"))

        self.stdout.write(self.style.SUCCESS("Restore tayyor!"))
