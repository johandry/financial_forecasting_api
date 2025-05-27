from datetime import datetime, timedelta
from types import SimpleNamespace
from app.core.forecasting import forecast_balance

def make_account(balance):
    return SimpleNamespace(current_balance=balance, id=1)

def make_bill(amount, start_date, recurrence=None, end_date=None):
    return SimpleNamespace(
        amount=amount,
        start_date=start_date,
        recurrence=recurrence,
        end_date=end_date,
    )

def make_tx(amount, date, is_recurring=False, recurrence=None, end_date=None):
    return SimpleNamespace(
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
    balances, alerts = forecast_balance(account, bills, transactions, horizon_days=3, buffer_amount=80)
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
    bills = [make_bill(20, datetime.combine(today, datetime.min.time()), "MONTHLY", None)]
    transactions = [
        make_tx(100, datetime.combine(today, datetime.min.time()), True, "MONTHLY", None)
    ]
    balances, alerts = forecast_balance(account, bills, transactions, horizon_days=32, buffer_amount=40)
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
    balances, alerts = forecast_balance(account, bills, transactions, horizon_days=3, buffer_amount=20)
    # Day 0: 30 - 15 = 15 (alert)
    assert (today + timedelta(days=0)) in alerts
    assert (today + timedelta(days=1)) in alerts
    assert (today + timedelta(days=2)) in alerts