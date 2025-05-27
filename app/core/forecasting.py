"""
Forecasting logic for account balances and cash flow.
Future implementation: forecast daily balances and buffer alerts.
"""

from datetime import datetime, timedelta
from collections import defaultdict
from app.core.recurrence import expand_recurrence


def forecast_balance(account, bills, transactions, horizon_days=90, buffer_amount=50.0):
    """
    Calculate daily balances for the next `horizon_days` days and alert dates below buffer.
    Args:
        account: Account object with current_balance and id.
        bills: List of Bill objects for the account.
        transactions: List of Transaction objects for the account.
        horizon_days: Number of days to forecast (default: 90).
        buffer_amount: User-configurable buffer threshold.
    Returns:
        Dict[date, balance]: Mapping of date to projected balance.
        List[date]: Dates when balance falls below buffer.
    """
    today = datetime.now().date()
    balances = {}
    # Start with today's balance
    balances[today] = account.current_balance

    # Collect all events (bills and transactions) by date
    events = defaultdict(float)
    end_date = today + timedelta(days=horizon_days - 1)

    # Expand and add bills
    for bill in bills:
        dates = expand_recurrence(
            bill.start_date.date(),
            bill.recurrence,
            bill.end_date.date() if bill.end_date else end_date,
        )
        for d in dates:
            d = d.date() if hasattr(d, "date") else d  # Ensure d is a date
            if today <= d <= end_date:
                events[d] -= bill.amount  # Bills are expenses

    # Expand and add transactions
    for tx in transactions:
        if tx.is_recurring and tx.recurrence:
            dates = expand_recurrence(
                tx.date.date(),
                tx.recurrence,
                tx.end_date.date() if tx.end_date else end_date,
            )
            for d in dates:
                d = d.date() if hasattr(d, "date") else d
                if today <= d <= end_date:
                    events[d] += tx.amount
        else:
            d = tx.date.date() if hasattr(tx.date, "date") else tx.date
            if today <= d <= end_date:
                events[d] += tx.amount

    # Calculate daily balances
    # Start with today's balance and apply today's events
    balances[today] = account.current_balance + events[today]
    last_balance = balances[today]
    alerts = []
    if last_balance < buffer_amount:
        alerts.append(today)
    for i in range(1, horizon_days):
        day = today + timedelta(days=i)
        last_balance += events[day]
        balances[day] = last_balance
        if last_balance < buffer_amount:
            alerts.append(day)

    return balances, alerts
