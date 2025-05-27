from datetime import datetime, timedelta
from types import SimpleNamespace
import pytest

from app.core.forecasting import forecast_balance


def make_account(balance, id=1):
    return SimpleNamespace(current_balance=balance, id=id)


def make_bill(amount, start_date, recurrence=None, end_date=None, id=1):
    return SimpleNamespace(
        id=id,
        amount=amount,
        start_date=start_date,
        recurrence=recurrence,
        end_date=end_date,
    )


def make_tx(amount, date, is_recurring=False, recurrence=None, end_date=None, id=1):
    return SimpleNamespace(
        id=id,
        amount=amount,
        date=date,
        is_recurring=is_recurring,
        recurrence=recurrence,
        end_date=end_date,
    )


def test_forecast_simple():
    today = datetime.now().date()
    account = make_account(100)
    bills = [make_bill(10, datetime.combine(today, datetime.min.time()), "DAILY", None)]
    transactions = [make_tx(5, datetime.combine(today, datetime.min.time()))]
    balances, alerts = forecast_balance(
        account, bills, transactions, horizon_days=3, buffer_amount=80
    )
    # Day 0: 100 + 5 - 10 = 95
    # Day 1: 95 - 10 = 85
    # Day 2: 85 - 10 = 75 (alert)
    assert balances[today] == 95
    assert balances[today + timedelta(days=1)] == 85
    assert balances[today + timedelta(days=2)] == 75
    assert (today + timedelta(days=2)) in alerts


def test_forecast_with_recurring_tx():
    today = datetime.now().date()
    account = make_account(50)
    bills = [
        make_bill(20, datetime.combine(today, datetime.min.time()), "MONTHLY", None)
    ]
    transactions = [
        make_tx(
            100, datetime.combine(today, datetime.min.time()), True, "MONTHLY", None
        )
    ]
    balances, alerts = forecast_balance(
        account, bills, transactions, horizon_days=32, buffer_amount=40
    )
    # Day 0: 50 + 100 - 20 = 130
    assert balances[today] == 130
    # Next month (should be 130 + 100 - 20 = 210)
    next_month = today + timedelta(days=31)
    assert balances[next_month] == 210


def test_forecast_alerts():
    today = datetime.now().date()
    account = make_account(30)
    bills = [make_bill(15, datetime.combine(today, datetime.min.time()), "DAILY", None)]
    transactions = []
    balances, alerts = forecast_balance(
        account, bills, transactions, horizon_days=3, buffer_amount=20
    )
    # Day 0: 30 - 15 = 15 (alert)
    assert (today + timedelta(days=0)) in alerts
    assert (today + timedelta(days=1)) in alerts
    assert (today + timedelta(days=2)) in alerts


def test_forecast_with_daily_bill_and_alert():
    today = datetime.now().date()
    account = make_account(100)
    bills = [make_bill(20, datetime.combine(today, datetime.min.time()), "DAILY")]
    transactions = []
    balances, alerts = forecast_balance(account, bills, transactions, horizon_days=4, buffer_amount=50)
    # Day 0: 100 - 20 = 80
    # Day 1: 80 - 20 = 60
    # Day 2: 60 - 20 = 40 (alert)
    assert balances[today] == 80
    assert balances[today + timedelta(days=1)] == 60
    assert balances[today + timedelta(days=2)] == 40
    assert (today + timedelta(days=2)) in alerts


def test_forecast_with_weekly_income_and_no_alert():
    today = datetime.now().date()
    account = make_account(50)
    bills = []
    transactions = [make_tx(30, datetime.combine(today, datetime.min.time()), True, "WEEKLY")]
    balances, alerts = forecast_balance(account, bills, transactions, horizon_days=8, buffer_amount=40)
    # Day 0: 50 + 30 = 80
    # Day 7: 80 + 30 = 110
    assert balances[today] == 80
    assert balances[today + timedelta(days=7)] == 110
    assert not alerts  # No day falls below buffer


def test_forecast_with_monthly_bill_and_alert():
    today = datetime.now().date()
    account = make_account(60)
    bills = [make_bill(50, datetime.combine(today, datetime.min.time()), "MONTHLY")]
    transactions = []
    balances, alerts = forecast_balance(account, bills, transactions, horizon_days=31, buffer_amount=20)
    # Day 0: 60 - 50 = 10 (alert)
    assert balances[today] == 10
    assert today in alerts


def test_forecast_with_eom_bill():
    today = datetime(2024, 1, 31).date()
    account = make_account(200)
    bills = [make_bill(100, datetime.combine(today, datetime.min.time()), "EOM")]
    transactions = []
    balances, alerts = forecast_balance(
        account, bills, transactions, horizon_days=62, buffer_amount=50, start_date=today
    )
    assert balances[today] == 100
    feb_29 = datetime(2024, 2, 29).date()
    assert balances[feb_29] == 0
    assert feb_29 in alerts


def test_forecast_with_multiple_bills_and_transactions():
    today = datetime.now().date()
    account = make_account(200)
    bills = [
        make_bill(50, datetime.combine(today, datetime.min.time()), "DAILY"),
        make_bill(100, datetime.combine(today, datetime.min.time()), "WEEKLY"),
    ]
    transactions = [
        make_tx(200, datetime.combine(today, datetime.min.time()), True, "MONTHLY"),
        make_tx(20, datetime.combine(today, datetime.min.time()), True, "DAILY"),
    ]
    balances, alerts = forecast_balance(account, bills, transactions, horizon_days=8, buffer_amount=100)
    assert any(bal < 100 for bal in balances.values())
    assert isinstance(alerts, list)


def test_forecast_with_no_events():
    today = datetime.now().date()
    account = make_account(100)
    bills = []
    transactions = []
    balances, alerts = forecast_balance(account, bills, transactions, horizon_days=5, buffer_amount=50)
    for i in range(5):
        assert balances[today + timedelta(days=i)] == 100
    assert not alerts


@pytest.mark.parametrize("recurrence,expected_dates", [
    ("DAILY",  [0, 1, 2]),
    ("WEEKLY", [0, 7, 14]),
    ("MONTHLY", [0, 31, 59]),  # Approximate for 2 months
])
def test_recurrence_expansion_in_forecast(recurrence, expected_dates):
    today = datetime(2024, 1, 1).date()
    account = make_account(100)
    bills = [make_bill(10, datetime.combine(today, datetime.min.time()), recurrence)]
    transactions = []
    balances, _ = forecast_balance(account, bills, transactions, horizon_days=61, buffer_amount=0, start_date=today)
    for offset in expected_dates:
        assert (today + timedelta(days=offset)) in balances


def test_forecast_with_overlapping_bills():
    today = datetime(2024, 2, 25).date()
    account = make_account(300)
    # Two bills: one daily, one weekly, both overlap on some days
    bills = [
        make_bill(20, datetime.combine(today, datetime.min.time()), "DAILY"),
        make_bill(50, datetime.combine(today, datetime.min.time()), "WEEKLY"),
    ]
    transactions = []
    balances, alerts = forecast_balance(account, bills, transactions, horizon_days=8, buffer_amount=100, start_date=today)
    # On day 0: 300 - 20 - 50 = 230
    assert balances[today] == 230
    # On day 1: 230 - 20 = 210
    assert balances[today + timedelta(days=1)] == 210
    # On day 7: 230 - 20*7 - 50 = 40 (alert)
    assert balances[today + timedelta(days=7)] == 40
    assert (today + timedelta(days=7)) in alerts


def test_forecast_eom_leap_year():
    # Feb 2024 is a leap year, EOM should hit Feb 29
    today = datetime(2024, 1, 31).date()
    account = make_account(500)
    bills = [make_bill(100, datetime.combine(today, datetime.min.time()), "EOM")]
    transactions = []
    balances, alerts = forecast_balance(account, bills, transactions, horizon_days=62, buffer_amount=200, start_date=today)
    jan_31 = today
    feb_29 = datetime(2024, 2, 29).date()
    mar_31 = datetime(2024, 3, 31).date()
    # Jan 31: 500 - 100 = 400
    assert balances[jan_31] == 400
    # Feb 29: 400 - 100 = 300
    assert balances[feb_29] == 300
    # Mar 31: 300 - 100 = 200 (alert)
    assert balances[mar_31] == 200
    assert mar_31 not in alerts  # Not below buffer
    # If buffer is increased, Mar 31 would be an alert
    balances2, alerts2 = forecast_balance(account, bills, transactions, horizon_days=62, buffer_amount=250, start_date=today)
    assert mar_31 in alerts2


def test_forecast_monthly_on_31st_skips_short_months():
    today = datetime(2024, 1, 31).date()
    account = make_account(300)
    bills = [make_bill(100, datetime.combine(today, datetime.min.time()), "MONTHLY")]
    transactions = []
    balances, alerts = forecast_balance(account, bills, transactions, horizon_days=90, buffer_amount=50, start_date=today)
    jan_31 = datetime(2024, 1, 31).date()
    mar_31 = datetime(2024, 3, 31).date()
    # Deduction on Jan 31
    assert balances[jan_31] == 200
    # Deduction on Mar 31
    assert balances[mar_31] == 100
    # No deduction in February (balance remains the same)
    feb_dates = [d for d in balances if d.month == 2 and d.year == 2024]
    feb_balances = [balances[d] for d in sorted(feb_dates)]
    assert all(b == feb_balances[0] for b in feb_balances)


def test_forecast_weekly_crossing_leap_day():
    today = datetime(2024, 2, 23).date()  # Friday before leap day
    account = make_account(100)
    bills = [make_bill(10, datetime.combine(today, datetime.min.time()), "WEEKLY")]
    transactions = []
    balances, alerts = forecast_balance(account, bills, transactions, horizon_days=14, buffer_amount=80, start_date=today)
    # Should have bills on Feb 23 and Mar 1 (crossing Feb 29)
    assert balances[today] == 90
    mar_1 = datetime(2024, 3, 1).date()
    assert mar_1 in balances


def test_forecast_daily_crossing_month_and_leap_day():
    today = datetime(2024, 2, 27).date()
    account = make_account(50)
    bills = [make_bill(10, datetime.combine(today, datetime.min.time()), "DAILY")]
    transactions = []
    balances, alerts = forecast_balance(account, bills, transactions, horizon_days=5, buffer_amount=20, start_date=today)
    # Feb 27: 50-10=40, Feb 28: 30, Feb 29: 20, Mar 1: 10 (alert)
    assert balances[today] == 40
    feb_29 = datetime(2024, 2, 29).date()
    assert balances[feb_29] == 20
    mar_1 = datetime(2024, 3, 1).date()
    assert balances[mar_1] == 10
    assert mar_1 in alerts


def test_forecast_eom_leap_year():
    # Feb 2024 is a leap year, EOM should hit Feb 29
    today = datetime(2024, 1, 31).date()
    account = make_account(500)
    bills = [make_bill(100, datetime.combine(today, datetime.min.time()), "EOM")]
    transactions = []
    balances, alerts = forecast_balance(account, bills, transactions, horizon_days=62, buffer_amount=200, start_date=today)
    jan_31 = datetime(2024, 1, 31).date()
    mar_31 = datetime(2024, 3, 31).date()
    assert balances[jan_31] == 400  # 500 - 100
    assert balances[mar_31] == 200  # 400 - 100
    # Check that no other day has a deduction (i.e., the balance doesn't decrease except on these two days)
    for d in balances:
        if d not in (jan_31, mar_31):
            prev = balances.get(d - timedelta(days=1), balances[jan_31])
            assert balances[d] == prev