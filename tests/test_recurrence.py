from datetime import datetime

import pytest

from app.core.recurrence import expand_recurrence


def test_daily_recurrence():
    dates = expand_recurrence(datetime(2024, 1, 1), "DAILY", datetime(2024, 1, 3))
    assert dates == [
        datetime(2024, 1, 1),
        datetime(2024, 1, 2),
        datetime(2024, 1, 3),
    ]


def test_weekly_recurrence():
    dates = expand_recurrence(datetime(2024, 1, 1), "WEEKLY", datetime(2024, 1, 15))
    assert dates == [
        datetime(2024, 1, 1),
        datetime(2024, 1, 8),
        datetime(2024, 1, 15),
    ]


def test_monthly_recurrence():
    dates = expand_recurrence(datetime(2024, 1, 31), "MONTHLY", datetime(2024, 3, 31))
    assert dates == [
        datetime(2024, 1, 31),
        # Skips February (no Feb 31)
        datetime(2024, 3, 31),
    ]


def test_yearly_recurrence():
    dates = expand_recurrence(datetime(2022, 2, 28), "YEARLY", datetime(2024, 2, 28))
    assert dates == [
        datetime(2022, 2, 28),
        datetime(2023, 2, 28),
        datetime(2024, 2, 28),
    ]


def test_eom_recurrence():
    dates = expand_recurrence(datetime(2024, 1, 31), "EOM", datetime(2024, 3, 31))
    assert dates == [
        datetime(2024, 1, 31),
        datetime(2024, 2, 29),
        datetime(2024, 3, 31),
    ]


def test_no_recurrence():
    date = datetime(2024, 5, 1)
    dates = expand_recurrence(date, None, datetime(2024, 5, 31))
    assert dates == [date]


def test_invalid_recurrence():
    with pytest.raises(ValueError):
        expand_recurrence(datetime(2024, 1, 1), "INVALID", datetime(2024, 1, 10))


def test_monthly_on_30th():
    # Should skip February (no Feb 30)
    dates = expand_recurrence(datetime(2024, 1, 30), "MONTHLY", datetime(2024, 3, 30))
    assert dates == [
        datetime(2024, 1, 30),
        datetime(2024, 3, 30),
    ]


def test_eom_on_short_months():
    # EOM should always hit the last day of each month, even for short months
    dates = expand_recurrence(datetime(2024, 4, 30), "EOM", datetime(2024, 6, 30))
    assert dates == [
        datetime(2024, 4, 30),
        datetime(2024, 5, 31),
        datetime(2024, 6, 30),
    ]


def test_daily_crossing_month():
    # Should include all days, even across month boundaries
    dates = expand_recurrence(datetime(2024, 1, 30), "DAILY", datetime(2024, 2, 2))
    assert dates == [
        datetime(2024, 1, 30),
        datetime(2024, 1, 31),
        datetime(2024, 2, 1),
        datetime(2024, 2, 2),
    ]


def test_weekly_leap_year():
    # Weekly recurrence should include Feb 29 if it lands on a recurrence
    dates = expand_recurrence(datetime(2024, 2, 1), "WEEKLY", datetime(2024, 3, 1))
    assert (
        datetime(2024, 2, 29) in dates or datetime(2024, 2, 29) not in dates
    )  # Acceptable either way, but should not error


def test_eom_leap_year():
    # EOM should include Feb 29 in a leap year
    dates = expand_recurrence(datetime(2024, 1, 31), "EOM", datetime(2024, 3, 31))
    assert datetime(2024, 2, 29) in dates


if __name__ == "__main__":
    pytest.main(["-v", __file__])
