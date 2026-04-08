import os
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Mavjud backuplarni ko'rsatish"

    def handle(self, *args, **options):
        backup_dir = os.path.join(settings.BASE_DIR, "backups")

        if not os.path.exists(backup_dir):
            self.stdout.write("Backup papkasi yo'q")
            return

        files = sorted(os.listdir(backup_dir), reverse=True)

        if not files:
            self.stdout.write("Hali backup yo'q. Yaratish: python manage.py backup_db")
            return

        self.stdout.write(self.style.SUCCESS(f"\nBackuplar ({len(files)} ta):\n"))
        self.stdout.write(f'{"Fayl":<40} {"Hajmi":<12} {"Sana"}')
        self.stdout.write("-" * 70)

        for file_name in files:
            filepath = os.path.join(backup_dir, file_name)
            size = os.path.getsize(filepath)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))

            if size > 1048576:
                size_str = f"{size / 1048576:.1f} MB"
            else:
                size_str = f"{size / 1024:.1f} KB"

            self.stdout.write(f'{file_name:<40} {size_str:<12} {mtime.strftime("%d.%m.%Y %H:%M")}')
