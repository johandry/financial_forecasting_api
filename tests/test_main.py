from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import TestingSessionLocal
from tests.helpers import (get_or_create_account, get_or_create_user,
                           get_or_create_user_settings)

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Financial Forecasting API" in response.json()["msg"]


def test_accounts_crud():
    # Ensure user exists
    db = TestingSessionLocal()
    user_id = get_or_create_user(db)
    db.close()

    # Create account
    payload = {
        "user_id": user_id,
        "name": "Test Account",
        "type": "checking",
        "current_balance": 100.0,
    }
    response = client.post("/accounts/", json=payload)
    assert response.status_code == 200
    account = response.json()
    assert account["name"] == "Test Account"

    # List accounts
    response = client.get("/accounts/")
    assert response.status_code == 200
    assert any(acc["name"] == "Test Account" for acc in response.json())

    # Soft-delete account
    response = client.delete(f"/accounts/{account['id']}")
    assert response.status_code == 200
    assert response.json()["deleted_at"] is not None


def test_bills_crud():
    # Ensure account exists
    db = TestingSessionLocal()
    account_id = get_or_create_account(db)
    db.close()

    # Create a bill (assume account_id 1 exists from seed)
    payload = {
        "account_id": account_id,
        "name": "Internet",
        "amount": 50.0,
        "start_date": "2024-01-01T00:00:00",
        "recurrence": "MONTHLY",
        "notes": "ISP bill",
    }
    response = client.post("/bills/", json=payload)
    assert response.status_code == 200
    bill = response.json()
    assert bill["name"] == "Internet"

    # List bills
    response = client.get("/bills/")
    assert response.status_code == 200
    assert any(b["name"] == "Internet" for b in response.json())

    # Soft-delete bill
    response = client.delete(f"/bills/{bill['id']}")
    assert response.status_code == 200
    assert response.json()["deleted_at"] is not None


def test_transactions_crud():
    # Ensure account exists
    db = TestingSessionLocal()
    account_id = get_or_create_account(db)
    db.close()

    payload = {
        "account_id": account_id,
        "name": "Deposit",
        "amount": 200.0,
        "date": "2024-01-02T00:00:00",
        "is_recurring": False,
        "notes": "Test deposit",
    }
    response = client.post("/transactions/", json=payload)
    assert response.status_code == 200
    transaction = response.json()
    assert transaction["name"] == "Deposit"

    # List transactions
    response = client.get("/transactions/")
    assert response.status_code == 200
    assert any(t["name"] == "Deposit" for t in response.json())

    # Soft-delete transaction
    response = client.delete(f"/transactions/{transaction['id']}")
    assert response.status_code == 200
    assert response.json()["deleted_at"] is not None


def test_user_settings_get_and_update():
    # Ensure user and settings exist
    db = TestingSessionLocal()
    user_id = get_or_create_user_settings(db)
    db.close()

    # Now run the test as before
    response = client.get("/user_settings/", params={"user_id": user_id})
    assert response.status_code == 200
    settings = response.json()
    assert "buffer_amount" in settings

    # Update user settings
    update = {"buffer_amount": 75.0, "forecast_horizon_months": 6}
    response = client.put("/user_settings/", params={"user_id": user_id}, json=update)
    assert response.status_code == 200
    assert response.json()["buffer_amount"] == 75.0
    assert response.json()["forecast_horizon_months"] == 6


def test_auth_login_success():
    # Ensure user exists
    db = TestingSessionLocal()
    _ = get_or_create_user(db)
    db.close()

    response = client.post(
        "/auth/login",
        data={"username": "johandry@example.com", "password": "$3cr3tP@a55w0rd!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_auth_login_failure():
    # Ensure user exists
    db = TestingSessionLocal()
    _ = get_or_create_user(db)
    db.close()

    response = client.post(
        "/auth/login",
        data={"username": "johandry@example.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"


# def test_rate_limit():
#     # Do not exceed the rate limit (assuming 100/min)
#     not_hit_429 = True
#     for _ in range(100):
#         response = client.get("/")
#         if response.status_code == 429:
#             not_hit_429 = False
#             break
#     assert not_hit_429, "Did not hit rate limit"

if __name__ == "__main__":
    import pytest

    pytest.main(["-v", __file__])
