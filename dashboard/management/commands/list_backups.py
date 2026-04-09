import os

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Backuplar ro'yxati"

    def handle(self, *args, **options):
        backup_dir = os.path.join(settings.BASE_DIR, "backups")
        if not os.path.exists(backup_dir):
            self.stdout.write("Backup yo'q")
            return

        files = sorted(os.listdir(backup_dir), reverse=True)
        if not files:
            self.stdout.write("Backup yo'q")
            return

        for file_name in files:
            path = os.path.join(backup_dir, file_name)
            size = os.path.getsize(path) / 1024
            self.stdout.write(f"  {file_name} ({size:.1f} KB)")
