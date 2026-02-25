from django.core.management.base import BaseCommand, CommandError

from core.db_sanity import run_db_sanity_checks


class Command(BaseCommand):
    help = "Run DB sanity checks for required tables, RPCs, policies, and smoke SELECTs."

    def handle(self, *args, **options):
        results = run_db_sanity_checks()

        missing_tables = results["missing_tables"]
        missing_rpcs = results["missing_rpcs"]
        tables_without_policies = results["tables_without_policies"]
        smoke_failures = results["smoke_failures"]

        if missing_tables:
            self.stdout.write(self.style.ERROR("Missing tables:"))
            for table in missing_tables:
                self.stdout.write(f"  - {table}")

        if missing_rpcs:
            self.stdout.write(self.style.ERROR("Missing RPCs:"))
            for rpc in missing_rpcs:
                self.stdout.write(f"  - {rpc}")

        if tables_without_policies:
            self.stdout.write(self.style.ERROR("Tables missing RLS policies:"))
            for table in tables_without_policies:
                self.stdout.write(f"  - {table}")

        if smoke_failures:
            self.stdout.write(self.style.ERROR("Smoke SELECT failures:"))
            for table, error in smoke_failures.items():
                self.stdout.write(f"  - {table}: {error}")

        if missing_tables or missing_rpcs or tables_without_policies or smoke_failures:
            raise CommandError("DB sanity checks failed.")

        self.stdout.write(self.style.SUCCESS("DB sanity checks passed."))
