"""
Recurrence logic for bills and transactions.

Provides a function to expand recurring events into individual dates using dateutil.rrule.
"""

from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from datetime import datetime
from dateutil.relativedelta import relativedelta

FREQ_MAP = {
    "DAILY": DAILY,
    "WEEKLY": WEEKLY,
    "MONTHLY": MONTHLY,
    "YEARLY": YEARLY,
    "EOM": MONTHLY,  # EOM handled specially below
}


def expand_recurrence(start_date, recurrence_rule, end_date=None):
    """
    Expand a recurring event into a list of occurrence dates.

    Args:
        start_date (datetime): The first occurrence date (user-specified).
        recurrence_rule (str): Recurrence pattern, e.g., "MONTHLY", "EOM".
        end_date (datetime, optional): The last possible occurrence date (user-specified).

    Returns:
        List[datetime]: List of occurrence datetimes.

    Examples:
        expand_recurrence(datetime(2024, 1, 31), "EOM", datetime(2024, 5, 31))
        expand_recurrence(datetime(2024, 1, 1), "WEEKLY", datetime(2024, 2, 1))
    """
    if not recurrence_rule:
        return [start_date]

    freq = FREQ_MAP.get(recurrence_rule.upper())
    if freq is None:
        raise ValueError(f"Unsupported recurrence rule: {recurrence_rule}")

    if recurrence_rule.upper() == "EOM":
        # End of month: generate monthly, then adjust to last day of each month
        occurrences = []
        current = start_date
        while not end_date or current <= end_date:
            # Move to last day of the month
            next_month = current.replace(day=28) + relativedelta(days=4)
            last_day = next_month - relativedelta(days=next_month.day)
            occurrences.append(last_day)
            current = last_day + relativedelta(months=1)
            if end_date and current > end_date:
                break
        return [dt for dt in occurrences if not end_date or dt <= end_date]

    rule = rrule(
        freq,
        dtstart=start_date,
        until=end_date
    )
    return list(rule)


