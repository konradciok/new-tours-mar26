from django.core.management.base import BaseCommand, CommandError

from core.verification import get_missing_frontend_read_requirements


class Command(BaseCommand):
    help = "Validate required seo_meta paths and site_settings keys for frontend reads."

    def handle(self, *args, **options):
        missing_paths, missing_keys = get_missing_frontend_read_requirements()

        if missing_paths:
            self.stdout.write(self.style.ERROR("Missing seo_meta.page_path entries:"))
            for path in missing_paths:
                self.stdout.write(f"  - {path}")

        if missing_keys:
            self.stdout.write(self.style.ERROR("Missing site_settings.key entries:"))
            for key in missing_keys:
                self.stdout.write(f"  - {key}")

        if missing_paths or missing_keys:
            raise CommandError("Frontend read requirements are incomplete.")

        self.stdout.write(
            self.style.SUCCESS("Frontend read requirements are complete.")
        )
