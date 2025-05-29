import time
import yaml
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from datetime import datetime

from app import models  # noqa: F401
from app.core.database import Base, SessionLocal, engine
from app.models import Account, Bill, Transaction, User, UserSettings
from app.core.security import get_password_hash

def seed_database(db: Session, data: dict):
    # Users
    users_map = {}
    for user in data.get("users", []):
        hashed_password = get_password_hash(user.get("password", "changeme"))
        user_obj = User(
            email=user["email"],
            hashed_password=hashed_password,
            is_active=user.get("is_active", True),
        )
        db.add(user_obj)
        db.flush()
        users_map[user["email"]] = user_obj

    # UserSettings
    for setting in data.get("user_settings", []):
        user_obj = users_map.get(setting["user_email"])
        if user_obj:
            settings_obj = UserSettings(
                user_id=user_obj.id,
                **{k: v for k, v in setting.items() if k != "user_email"},
            )
            db.add(settings_obj)

    # Accounts
    accounts_map = {}
    for account in data.get("accounts", []):
        user_obj = users_map.get(account["user_email"])
        if user_obj:
            account_obj = Account(
                user_id=user_obj.id,
                name=account["name"],
                type=account.get("type"),
                current_balance=account.get("current_balance", 0.0),
            )
            db.add(account_obj)
            db.flush()
            accounts_map[account["name"]] = account_obj

    # Bills
    for bill in data.get("bills", []):
        account_obj = accounts_map.get(bill["account_name"])
        if account_obj:
            end_date = bill.get("end_date")
            # Convert end_date to a datetime object if it's not None
            end_date = datetime.fromisoformat(end_date) if end_date else None
            bill_obj = Bill(
                account_id=account_obj.id,
                name=bill["name"],
                amount=bill["amount"],
                start_date=datetime.fromisoformat(bill["start_date"]),
                end_date=end_date,
                recurrence=bill.get("recurrence"),
                notes=bill.get("notes"),
            )
            db.add(bill_obj)

    # Transactions
    for txn in data.get("transactions", []):
        account_obj = accounts_map.get(txn["account_name"])
        if account_obj:
            end_date = txn.get("end_date")
            # Convert end_date to a datetime object if it's not None
            end_date = datetime.fromisoformat(end_date) if end_date else None
            txn_obj = Transaction(
                account_id=account_obj.id,
                name=txn["name"],
                amount=txn["amount"],
                date=datetime.fromisoformat(txn["date"]),
                is_recurring=txn.get("is_recurring", False),
                end_date=end_date,
                recurrence=txn.get("recurrence"),
                notes=txn.get("notes"),
            )
            db.add(txn_obj)

    db.commit()
    db.close()
    print("Database seeded successfully.")

def wait_for_db(engine, timeout=30):
    start = time.time()
    while True:
        try:
            with engine.connect():
                return
        except OperationalError:
            if time.time() - start > timeout:
                raise
            time.sleep(1)

def load_yaml_data(filepath):
    with open(filepath, "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    import sys

    wait_for_db(engine)
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    data_file = "seed_data.yaml"
    if len(sys.argv) == 2:
        data_file = str(sys.argv[1])

    data = load_yaml_data(data_file)
    if not data:
        print("No data found in the provided YAML file.")
        sys.exit(1)
    seed_database(db=db, data=data)
