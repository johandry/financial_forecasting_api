from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.forecasting import forecast_balance
from app.core.recurrence import expand_recurrence
from app.models import Account, Bill, ForecastOverride, Transaction
from app.schemas import ForecastOverrideCreate

router = APIRouter()


def get_account_data(db: Session, account_id: int):
    account = db.query(Account).filter(Account.id == account_id).first()
    bills = db.query(Bill).filter(Bill.account_id == account_id).all()
    transactions = (
        db.query(Transaction).filter(Transaction.account_id == account_id).all()
    )
    return account, bills, transactions


@router.get("/forecast")
def get_forecast(
    account_id: int = Query(...),
    months: int = Query(3, ge=1, le=12),
    buffer: float = Query(50.0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Returns projected daily balances and upcoming events for the given account.
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


@router.post("/overrides")
def create_override(
    override: ForecastOverrideCreate,
    db: Session = Depends(get_db),
):
    """
    Create or update a forecast override (skip or modify a specific event).
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
