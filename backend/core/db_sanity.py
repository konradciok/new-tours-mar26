from django.db import connection

REQUIRED_TABLES = [
    "tours",
    "destinations",
    "tour_destinations",
    "blog_posts",
    "travel_styles",
    "testimonials",
    "faq",
    "contact_submissions",
    "seo_meta",
    "site_settings",
]

REQUIRED_RPCS = ["increment_blog_view"]


def evaluate_db_sanity(
    existing_tables: set[str],
    existing_rpcs: set[str],
    policy_tables: set[str],
    smoke_failures: dict[str, str],
) -> dict[str, list[str] | dict[str, str]]:
    return {
        "missing_tables": [table for table in REQUIRED_TABLES if table not in existing_tables],
        "missing_rpcs": [rpc for rpc in REQUIRED_RPCS if rpc not in existing_rpcs],
        "tables_without_policies": [table for table in REQUIRED_TABLES if table not in policy_tables],
        "smoke_failures": smoke_failures,
    }


def check_table_select_smoke(table_names: list[str]) -> dict[str, str]:
    failures: dict[str, str] = {}
    for table in table_names:
        try:
            with connection.cursor() as cursor:
                cursor.execute(f'SELECT 1 FROM "{table}" LIMIT 1')
        except Exception as exc:  # pragma: no cover - exercised by mock-based tests
            failures[table] = str(exc)
    return failures


def run_db_sanity_checks() -> dict[str, list[str] | dict[str, str]]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
              AND tablename = ANY(%s)
            """,
            [REQUIRED_TABLES],
        )
        existing_tables = {row[0] for row in cursor.fetchall()}

        cursor.execute(
            """
            SELECT p.proname
            FROM pg_proc p
            JOIN pg_namespace n ON n.oid = p.pronamespace
            WHERE n.nspname = 'public'
              AND p.proname = ANY(%s)
            """,
            [REQUIRED_RPCS],
        )
        existing_rpcs = {row[0] for row in cursor.fetchall()}

        cursor.execute(
            """
            SELECT DISTINCT tablename
            FROM pg_policies
            WHERE schemaname = 'public'
              AND tablename = ANY(%s)
            """,
            [REQUIRED_TABLES],
        )
        policy_tables = {row[0] for row in cursor.fetchall()}

    smoke_failures = check_table_select_smoke(REQUIRED_TABLES)
    return evaluate_db_sanity(existing_tables, existing_rpcs, policy_tables, smoke_failures)
