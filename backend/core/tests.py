import os
from unittest.mock import MagicMock, call, patch

import django
from unittest import TestCase
from django.core.exceptions import ValidationError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import ContactSubmission, SiteSetting, Testimonial, Tour
from core.tour_destinations import list_destination_ids_for_tour, replace_tour_destinations


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
