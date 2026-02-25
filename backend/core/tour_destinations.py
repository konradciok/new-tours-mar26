from collections.abc import Iterable

from django.db import connection, transaction


def list_destination_ids_for_tour(tour_id: int) -> list[int]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT destination_id
            FROM tour_destinations
            WHERE tour_id = %s
            ORDER BY destination_id
            """,
            [tour_id],
        )
        rows = cursor.fetchall()
    return [int(row[0]) for row in rows]


def replace_tour_destinations(tour_id: int, destination_ids: Iterable[int]) -> None:
    unique_destination_ids: list[int] = []
    seen: set[int] = set()

    for destination_id in destination_ids:
        normalized_id = int(destination_id)
        if normalized_id in seen:
            continue
        seen.add(normalized_id)
        unique_destination_ids.append(normalized_id)

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM tour_destinations WHERE tour_id = %s", [tour_id])
            for destination_id in unique_destination_ids:
                cursor.execute(
                    """
                    INSERT INTO tour_destinations (tour_id, destination_id)
                    VALUES (%s, %s)
                    """,
                    [tour_id, destination_id],
                )
