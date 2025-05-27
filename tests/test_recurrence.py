from datetime import datetime
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
        # datetime(2024, 2, 29),  # This will NOT be present for "MONTHLY"
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

if __name__ == "__main__":
    import pytest

    pytest.main(["-v", __file__])