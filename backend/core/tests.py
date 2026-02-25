from unittest.mock import MagicMock, call, patch

from unittest import TestCase

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
