import os
from io import StringIO
from unittest.mock import MagicMock, call, patch

import django
from unittest import TestCase
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.admin import BlogPostAdmin, ContactSubmissionAdmin, TourAdmin
from core.db_sanity import check_table_select_smoke, evaluate_db_sanity
from core.models import BlogPost, ContactSubmission, SiteSetting, Testimonial, Tour
from core.tour_destinations import list_destination_ids_for_tour, replace_tour_destinations
from core.verification import REQUIRED_SEO_PATHS, REQUIRED_SITE_SETTING_KEYS, get_missing_frontend_read_requirements


class TourDestinationHelpersTests(TestCase):
    @patch("core.tour_destinations.connection.cursor")
    def test_list_destination_ids_for_tour(self, cursor_factory):
        cursor_cm = MagicMock()
        cursor = MagicMock()
        cursor_cm.__enter__.return_value = cursor
        cursor_factory.return_value = cursor_cm
        cursor.fetchall.return_value = [(4,), (9,), (12,)]

        result = list_destination_ids_for_tour(15)

        self.assertEqual(result, [4, 9, 12])
        cursor.execute.assert_called_once_with(
            """
            SELECT destination_id
            FROM tour_destinations
            WHERE tour_id = %s
            ORDER BY destination_id
            """,
            [15],
        )

    @patch("core.tour_destinations.transaction.atomic")
    @patch("core.tour_destinations.connection.cursor")
    def test_replace_tour_destinations_replaces_and_deduplicates(self, cursor_factory, atomic):
        atomic.return_value = MagicMock()

        cursor_cm = MagicMock()
        cursor = MagicMock()
        cursor_cm.__enter__.return_value = cursor
        cursor_factory.return_value = cursor_cm

        replace_tour_destinations(7, [3, 8, 3, 12])

        self.assertEqual(
            cursor.execute.call_args_list,
            [
                call("DELETE FROM tour_destinations WHERE tour_id = %s", [7]),
                call(
                    """
                    INSERT INTO tour_destinations (tour_id, destination_id)
                    VALUES (%s, %s)
                    """,
                    [7, 3],
                ),
                call(
                    """
                    INSERT INTO tour_destinations (tour_id, destination_id)
                    VALUES (%s, %s)
                    """,
                    [7, 8],
                ),
                call(
                    """
                    INSERT INTO tour_destinations (tour_id, destination_id)
                    VALUES (%s, %s)
                    """,
                    [7, 12],
                ),
            ],
        )


class ModelValidationTests(TestCase):
    def test_contact_submission_type_must_be_allowed(self):
        submission = ContactSubmission(type="invalid", name="A", email="a@example.com", payload={})

        with self.assertRaises(ValidationError):
            submission.clean()

    def test_testimonial_rating_must_be_in_range(self):
        testimonial = Testimonial(name="A", rating=6)

        with self.assertRaises(ValidationError):
            testimonial.full_clean(exclude=["date", "location", "text", "tour", "avatar"])

    @patch("core.models.TravelStyle.objects.filter")
    def test_tour_category_must_match_existing_travel_style_slug(self, filter_mock):
        filter_mock.return_value.exists.return_value = False
        tour = Tour(title="T", slug="t", category="missing-style")

        with self.assertRaises(ValidationError):
            tour.clean()

    def test_site_setting_string_keys_require_string_value(self):
        setting = SiteSetting(key="site_name", value={"not": "string"})

        with self.assertRaises(ValidationError):
            setting.clean()

    def test_site_setting_footer_links_requires_expected_shape(self):
        setting = SiteSetting(key="footer_links", value={"Explore": [{"label": "Tours"}]})

        with self.assertRaises(ValidationError):
            setting.clean()

    def test_site_setting_footer_links_accepts_valid_shape(self):
        setting = SiteSetting(
            key="footer_links",
            value={"Explore": [{"label": "Tours", "href": "/tours"}]},
        )

        setting.clean()


class FrontendReadinessVerificationTests(TestCase):
    @patch("core.verification.SeoMeta.objects.values_list")
    @patch("core.verification.SiteSetting.objects.values_list")
    def test_reports_missing_paths_and_keys(self, site_values_list, seo_values_list):
        seo_values_list.return_value = ["/", "/tours", "/blog"]
        site_values_list.return_value = ["site_name", "tagline", "email"]

        missing_paths, missing_keys = get_missing_frontend_read_requirements()

        self.assertIn("/destinations", missing_paths)
        self.assertIn("phone", missing_keys)

    @patch("core.verification.SeoMeta.objects.values_list")
    @patch("core.verification.SiteSetting.objects.values_list")
    def test_reports_no_missing_items_when_complete(self, site_values_list, seo_values_list):
        seo_values_list.return_value = REQUIRED_SEO_PATHS
        site_values_list.return_value = REQUIRED_SITE_SETTING_KEYS

        missing_paths, missing_keys = get_missing_frontend_read_requirements()

        self.assertEqual(missing_paths, [])
        self.assertEqual(missing_keys, [])

    @patch("core.management.commands.validate_frontend_readiness.get_missing_frontend_read_requirements")
    def test_management_command_fails_on_missing_items(self, missing_requirements_mock):
        missing_requirements_mock.return_value = (["/about"], ["site_name"])

        with self.assertRaises(CommandError):
            call_command("validate_frontend_readiness")

    @patch("core.management.commands.validate_frontend_readiness.get_missing_frontend_read_requirements")
    def test_management_command_succeeds_when_complete(self, missing_requirements_mock):
        missing_requirements_mock.return_value = ([], [])
        output = StringIO()

        call_command("validate_frontend_readiness", stdout=output)

        self.assertIn("Frontend read requirements are complete.", output.getvalue())


class AdminWorkflowTests(TestCase):
    @patch("core.admin.replace_tour_destinations")
    @patch("core.admin.admin.ModelAdmin.save_model")
    def test_tour_admin_save_model_syncs_destinations(self, base_save_model, replace_destinations):
        tour_admin = TourAdmin(Tour, AdminSite())
        request = MagicMock()
        obj = MagicMock()
        obj.id = 42

        destination_a = MagicMock()
        destination_a.id = 7
        destination_b = MagicMock()
        destination_b.id = 11
        form = MagicMock()
        form.cleaned_data = {"destinations": [destination_a, destination_b]}

        tour_admin.save_model(request, obj, form, change=True)

        base_save_model.assert_called_once_with(request, obj, form, True)
        replace_destinations.assert_called_once_with(42, [7, 11])

    def test_contact_submission_admin_is_read_only(self):
        admin_instance = ContactSubmissionAdmin(ContactSubmission, AdminSite())
        request = MagicMock()

        self.assertFalse(admin_instance.has_add_permission(request))
        self.assertFalse(admin_instance.has_change_permission(request))
        self.assertFalse(admin_instance.has_delete_permission(request))

    @patch("core.admin.timezone.now")
    def test_blog_publish_action_sets_published_at(self, timezone_now):
        timezone_now.return_value = "NOW"
        admin_instance = BlogPostAdmin(BlogPost, AdminSite())
        request = MagicMock()
        queryset = MagicMock()
        queryset.update.return_value = 3
        admin_instance.message_user = MagicMock()

        admin_instance.publish_posts(request, queryset)

        queryset.update.assert_called_once_with(published=True, published_at="NOW")
        admin_instance.message_user.assert_called_once_with(request, "Published 3 blog post(s).")

    def test_blog_unpublish_action_clears_published_at(self):
        admin_instance = BlogPostAdmin(BlogPost, AdminSite())
        request = MagicMock()
        queryset = MagicMock()
        queryset.update.return_value = 2
        admin_instance.message_user = MagicMock()

        admin_instance.unpublish_posts(request, queryset)

        queryset.update.assert_called_once_with(published=False, published_at=None)
        admin_instance.message_user.assert_called_once_with(request, "Unpublished 2 blog post(s).")


class DBSanityTests(TestCase):
    def test_evaluate_db_sanity_reports_missing_items(self):
        results = evaluate_db_sanity(
            existing_tables={"tours"},
            existing_rpcs=set(),
            policy_tables={"tours"},
            smoke_failures={"faq": "permission denied"},
        )

        self.assertIn("destinations", results["missing_tables"])
        self.assertIn("increment_blog_view", results["missing_rpcs"])
        self.assertIn("destinations", results["tables_without_policies"])
        self.assertEqual(results["smoke_failures"], {"faq": "permission denied"})

    @patch("core.db_sanity.connection.cursor")
    def test_check_table_select_smoke_reports_table_errors(self, cursor_factory):
        ok_cursor_cm = MagicMock()
        ok_cursor = MagicMock()
        ok_cursor_cm.__enter__.return_value = ok_cursor

        failing_cursor_cm = MagicMock()
        failing_cursor = MagicMock()
        failing_cursor.execute.side_effect = RuntimeError("relation missing")
        failing_cursor_cm.__enter__.return_value = failing_cursor

        cursor_factory.side_effect = [ok_cursor_cm, failing_cursor_cm]

        failures = check_table_select_smoke(["tours", "faq"])

        self.assertEqual(failures, {"faq": "relation missing"})

    @patch("core.management.commands.validate_db_sanity.run_db_sanity_checks")
    def test_db_sanity_command_fails_when_checks_fail(self, run_checks):
        run_checks.return_value = {
            "missing_tables": ["faq"],
            "missing_rpcs": [],
            "tables_without_policies": [],
            "smoke_failures": {},
        }

        with self.assertRaises(CommandError):
            call_command("validate_db_sanity")

    @patch("core.management.commands.validate_db_sanity.run_db_sanity_checks")
    def test_db_sanity_command_succeeds_when_checks_pass(self, run_checks):
        run_checks.return_value = {
            "missing_tables": [],
            "missing_rpcs": [],
            "tables_without_policies": [],
            "smoke_failures": {},
        }
        output = StringIO()

        call_command("validate_db_sanity", stdout=output)

        self.assertIn("DB sanity checks passed.", output.getvalue())
