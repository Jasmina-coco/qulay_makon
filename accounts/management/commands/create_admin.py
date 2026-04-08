from django.core.management.base import BaseCommand

from accounts.models import CustomUser


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if not CustomUser.objects.filter(username="havo_quyoshli").exists():
            CustomUser.objects.create_superuser(
                username="havo_quyoshli",
                email="admin@marketplace.uz",
                password="havo_bulutli",
                role="admin",
                is_verified=True,
            )
            self.stdout.write(
                self.style.SUCCESS("Admin yaratildi: havo_quyoshli / havo_bulutli")
            )
        else:
            self.stdout.write("Admin allaqachon mavjud")
