import subprocess

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Git commit + baza backup = to'liq save point"

    def add_arguments(self, parser):
        parser.add_argument("message", type=str, nargs="?", default="save point", help="Commit xabari")

    def handle(self, *args, **options):
        message = options["message"]

        self.stdout.write("\n1) Baza backup...")
        call_command("backup_db", format="both")

        self.stdout.write("\n2) Git commit...")
        try:
            subprocess.run(["git", "add", "."], capture_output=True, check=True)
            result = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True)
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS(f"Git: {message}"))
            else:
                self.stdout.write(self.style.WARNING(f"Git: {result.stdout.strip()}"))
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING("Git o'rnatilmagan"))
        except subprocess.CalledProcessError as error:
            self.stdout.write(self.style.WARNING(f"Git add xato: {error}"))

        self.stdout.write(self.style.SUCCESS("\nSave point yaratildi!"))
