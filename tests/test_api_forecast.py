from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import TestingSessionLocal

client = TestClient(app)


def make_account(db, user_id, balance=100):
    from app.models import Account

    account = Account(name="Test", current_balance=balance, user_id=user_id)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def make_bill(db, account_id, amount, start_date, recurrence=None, end_date=None):
    from app.models import Bill

    bill = Bill(
        account_id=account_id,
        name="Test Bill",
        amount=amount,
        start_date=start_date,
        recurrence=recurrence,
        end_date=end_date,
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill


def make_tx(
    db, account_id, amount, date, is_recurring=False, recurrence=None, end_date=None
):
    from app.models import Transaction

    tx = Transaction(
        account_id=account_id,
        name="Test Tx",
        amount=amount,
        date=date,
        is_recurring=is_recurring,
        recurrence=recurrence,
        end_date=end_date,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def make_user(db, email="test@example.com"):
    from app.models import User

    user = User(email=email, hashed_password="fake", is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_forecast_and_alerts_endpoints():
    db = TestingSessionLocal()
    today = datetime.now()
    user = make_user(db)
    account = make_account(db, user_id=user.id, balance=100)
    make_bill(db, account.id, 10, today, "DAILY")
    make_tx(db, account.id, 5, today)
    account_id = account.id  # Store the id before closing the session
    db.close()

    # Test /forecast
    response = client.get(f"/forecast?account_id={account_id}&months=1&buffer=80")
    assert response.status_code == 200
    data = response.json()
    assert "balances" in data
    assert "alerts" in data
    assert "events" in data
    assert any(float(bal) < 80 for bal in data["balances"].values())

    # Test /alerts
    response = client.get(f"/alerts?account_id={account_id}&months=1&buffer=80")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert isinstance(data["alerts"], list)


def test_create_override():
    db = TestingSessionLocal()
    today = datetime.now()
    # Setup: create user, account, bill
    user = make_user(db)
    account = make_account(db, user_id=user.id, balance=100)
    bill = make_bill(db, account.id, 10, today, "DAILY")
    # Store IDs before closing session
    user_id = user.id
    account_id = account.id
    bill_id = bill.id
    db.close()

    # Test creating an override (skip the bill for today)
    payload = {
        "user_id": user_id,
        "account_id": account_id,
        "event_type": "bill",
        "event_id": bill_id,
        "event_date": today.date().isoformat(),
        "skip": True,
        "override_amount": None,
    }
    response = client.post("/overrides", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "override saved"
    assert "override_id" in data
