from src.quality_rules import is_valid_trip, payment_type_label, tip_percentage


def test_valid_trip_rule_accepts_normal_trip() -> None:
    assert is_valid_trip(1, 2.5, 14.0, 18.4)


def test_valid_trip_rule_rejects_bad_values() -> None:
    assert not is_valid_trip(0, 2.5, 14.0, 18.4)
    assert not is_valid_trip(1, 0, 14.0, 18.4)
    assert not is_valid_trip(1, 2.5, -1.0, 18.4)
    assert not is_valid_trip(1, 2.5, 14.0, None)


def test_tip_percentage() -> None:
    assert tip_percentage(2.5, 10.0) == 25.0
    assert tip_percentage(2.5, 0.0) == 0.0


def test_payment_type_label() -> None:
    assert payment_type_label(1) == "Credit card"
    assert payment_type_label("2") == "Cash"
    assert payment_type_label(99) == "Unknown"

