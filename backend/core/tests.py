import os
from io import StringIO
from unittest.mock import MagicMock, call, patch

import django
from unittest import TestCase
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import ContactSubmission, SiteSetting, Testimonial, Tour
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
