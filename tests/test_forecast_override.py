from datetime import datetime
from types import SimpleNamespace

from app.core.forecasting import forecast_balance
from app.models import ForecastOverride
from tests.conftest import TestingSessionLocal


def make_account(balance):
    return SimpleNamespace(current_balance=balance, id=1)


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


def test_forecast_with_override_skip():
    db = TestingSessionLocal()
    today = datetime.now()
    account = make_account(100)
    bill = make_bill(10, today, "DAILY", None, id=1)
    # Insert an override to skip the bill on today
    override = ForecastOverride(
        account_id=account.id,
        event_type="bill",
        event_id=1,
        event_date=today.date(),
        skip=True,
        override_amount=None,
        user_id=1,
    )
    db.add(override)
    db.commit()
    balances, alerts = forecast_balance(
        account, [bill], [], horizon_days=2, buffer_amount=80, db=db
    )
    db.close()
    # Bill should be skipped, so balance remains 100
    assert balances[today.date()] == 100


def test_forecast_with_override_amount():
    db = TestingSessionLocal()
    today = datetime.now()
    account = make_account(100)
    bill = make_bill(10, today, "DAILY", None, id=2)
    # Insert an override to change the bill amount to 2 on today
    override = ForecastOverride(
        account_id=account.id,
        event_type="bill",
        event_id=2,
        event_date=today.date(),
        skip=False,
        override_amount=2,
        user_id=1,
    )
    db.add(override)
    db.commit()
    balances, alerts = forecast_balance(
        account, [bill], [], horizon_days=2, buffer_amount=80, db=db
    )
    db.close()
    # Bill should be 2 instead of 10, so balance is 98
    assert balances[today.date()] == 98


if __name__ == "__main__":
    import pytest

    pytest.main(["-v", __file__])
