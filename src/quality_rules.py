from __future__ import annotations


def is_valid_trip(
    passenger_count: int | float | None,
    trip_distance: int | float | None,
    fare_amount: int | float | None,
    total_amount: int | float | None,
) -> bool:
    values = [passenger_count, trip_distance, fare_amount, total_amount]
    if any(value is None for value in values):
        return False

    return (
        1 <= float(passenger_count) <= 8
        and float(trip_distance) > 0
        and float(fare_amount) >= 0
        and float(total_amount) >= 0
    )


def tip_percentage(tip_amount: int | float, fare_amount: int | float) -> float:
    if fare_amount <= 0:
        return 0.0
    return round((tip_amount / fare_amount) * 100, 2)


def payment_type_label(payment_type: int | str | None) -> str:
    mapping = {
        "1": "Credit card",
        "2": "Cash",
        "3": "No charge",
        "4": "Dispute",
        "5": "Unknown",
        "6": "Voided trip",
    }
    return mapping.get(str(payment_type), "Unknown")

