from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict

from app.core.database import get_db
from app.core.forecasting import forecast_balance
from app.core.recurrence import expand_recurrence
from app.models import Account, Bill, ForecastOverride, Transaction
from app.schemas import ForecastOverrideCreate, ForecastResponse

router = APIRouter()


def get_account_data(db: Session, account_id: int):
    account = db.query(Account).filter(Account.id == account_id).first()
    bills = db.query(Bill).filter(Bill.account_id == account_id).all()
    transactions = (
        db.query(Transaction).filter(Transaction.account_id == account_id).all()
    )
    return account, bills, transactions


@router.get(
    "/forecast",
    response_model=ForecastResponse,
    summary="Get forecast balances and alerts",
    description="""
Returns projected daily balances and alert dates for an account, considering bills, transactions, and overrides.

**Example usage:**

- **Forecast for 3 months with a $50 buffer:**
    ```
    GET /forecast?account_id=1&months=3&buffer=50
    ```

- **Sample response:**
    ```json
    {
      "balances": {
        "2024-06-01": 100.0,
        "2024-06-02": 90.0,
        "2024-06-03": 80.0
      },
      "alerts": ["2024-06-03"],
      "events": [
        {"type": "bill", "name": "Rent", "amount": 1000, "date": "2024-06-01"},
        {"type": "transaction", "name": "Paycheck", "amount": 2000, "date": "2024-06-02"}
      ]
    }
    ```
""",
)
def get_forecast(
    account_id: int = Query(..., description="Account ID to forecast"),
    months: int = Query(3, ge=1, le=12, description="Number of months to forecast"),
    buffer: float = Query(50.0, ge=0, description="Buffer threshold for alerts"),
    db: Session = Depends(get_db),
):
    """
    Get forecast balances and alerts for an account.

    **Recurrence usage example:**
    - A bill with `recurrence="MONTHLY"` and `start_date="2024-01-31"` will be forecasted for the last day of each month (e.g., Jan 31, Mar 31, skipping February if no Feb 31).
    - A transaction with `recurrence="WEEKLY"` and `date="2024-06-01"` will repeat every 7 days.
    """
    account, bills, transactions = get_account_data(db, account_id)
    if not account:
        return {"error": "Account not found"}
    horizon_days = months * 30
    balances, alerts = forecast_balance(
        account, bills, transactions, horizon_days, buffer
    )
    # Collect upcoming events (bills and transactions) in the forecast window
    today = datetime.now().date()
    end_date = today + timedelta(days=horizon_days - 1)
    events = []
    for bill in bills:
        dates = [
            d.date() if hasattr(d, "date") else d
            for d in expand_recurrence(
                bill.start_date.date(),
                bill.recurrence,
                bill.end_date.date() if bill.end_date else end_date,
            )
        ]
        for d in dates:
            if today <= d <= end_date:
                events.append(
                    {
                        "type": "bill",
                        "name": bill.name,
                        "amount": bill.amount,
                        "date": d,
                    }
                )
    for tx in transactions:
        if tx.is_recurring and tx.recurrence:
            dates = [
                d.date() if hasattr(d, "date") else d
                for d in forecast_balance.expand_recurrence(
                    tx.date.date(),
                    tx.recurrence,
                    tx.end_date.date() if tx.end_date else end_date,
                )
            ]
            for d in dates:
                if today <= d <= end_date:
                    events.append(
                        {
                            "type": "transaction",
                            "name": tx.name,
                            "amount": tx.amount,
                            "date": d,
                        }
                    )
        else:
            d = tx.date.date() if hasattr(tx.date, "date") else tx.date
            if today <= d <= end_date:
                events.append(
                    {
                        "type": "transaction",
                        "name": tx.name,
                        "amount": tx.amount,
                        "date": d,
                    }
                )
    return {
        "balances": {str(k): v for k, v in balances.items()},
        "alerts": [str(d) for d in alerts],
        "events": events,
    }


@router.get("/alerts")
def get_alerts(
    account_id: int = Query(...),
    months: int = Query(3, ge=1, le=12),
    buffer: float = Query(50.0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Returns dates when projected balances fall below the buffer.
    """
    account, bills, transactions = get_account_data(db, account_id)
    if not account:
        return {"error": "Account not found"}
    horizon_days = months * 30
    _, alerts = forecast_balance(account, bills, transactions, horizon_days, buffer)
    return {"alerts": [str(d) for d in alerts]}


@router.post(
    "/overrides",
    response_model=Dict[str, int],
    summary="Create or update a forecast override",
    description="""
Create or update an override to skip or modify a specific bill or transaction on a given date.

**Example usage:**

- **Skip a bill on a specific date:**
    ```json
    {
      "user_id": 1,
      "account_id": 1,
      "event_type": "bill",
      "event_id": 10,
      "event_date": "2024-06-15",
      "skip": true
    }
    ```

- **Override a transaction amount:**
    ```json
    {
      "user_id": 1,
      "account_id": 1,
      "event_type": "transaction",
      "event_id": 5,
      "event_date": "2024-06-10",
      "override_amount": 500.0
    }
    ```
"""
)
def create_override(
    override: ForecastOverrideCreate,
    db: Session = Depends(get_db),
):
    """
    Create or update a forecast override (skip or modify a specific event).

    **Example:**  
    To skip a bill on 2024-06-15, send:
    ```
    {
      "user_id": 1,
      "account_id": 1,
      "event_type": "bill",
      "event_id": 10,
      "event_date": "2024-06-15",
      "skip": true
    }
    ```
    """
    obj = (
        db.query(ForecastOverride)
        .filter_by(
            user_id=override.user_id,
            account_id=override.account_id,
            event_type=override.event_type,
            event_id=override.event_id,
            event_date=override.event_date,
        )
        .first()
    )
    if obj:
        obj.skip = override.skip
        obj.override_amount = override.override_amount
    else:
        obj = ForecastOverride(**override.model_dump())
        db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"status": "override saved", "override_id": obj.id}
