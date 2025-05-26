import time
import datetime

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app import models  # Ensures all models are registered with Base
from app.core.database import Base, SessionLocal, engine
from app.models import Account, User, UserSettings, Bill, Transaction

def wait_for_db(engine, timeout=30):
    start = time.time()
    while True:
        try:
            with engine.connect() as conn:
                return
        except OperationalError:
            if time.time() - start > timeout:
                raise
            time.sleep(1)

def add_user(db: Session):
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("$3cr3tP@a55w0rd!")
    user = User(
        email="johandry@example.com",
        hashed_password=hashed_password,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id

def add_user_settings(db: Session, user_id: int):
    settings = UserSettings(
        user_id=user_id, buffer_amount=50.0, forecast_horizon_months=3
    )
    db.add(settings)
    db.commit()

def add_account(db: Session, user_id: int, name: str = "Checking", type: str = "checking", current_balance: float = 0.0):
    account = Account(
        user_id=user_id,
        name=name,
        type=type,
        current_balance=current_balance,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account.id

def add_bill(db: Session, account_id: int, name: str, amount: float, start_date: datetime.datetime, recurrence: str, notes: str = None):
    bill = Bill(
        account_id=account_id,
        name=name,
        amount=amount,
        start_date=start_date,
        recurrence=recurrence,
        notes=notes,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill.id

def add_transaction(db: Session, account_id: int, name: str, amount: float, date: datetime.datetime, is_recurring: bool = False, notes: str = None):
    transaction = Transaction(
        account_id=account_id,
        name=name,
        amount=amount,
        date=date,
        is_recurring=is_recurring,
        notes=notes,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction.id

def seed():
    db: Session = SessionLocal()
    user = db.query(User).first()

    if user is not None:
        db.close()
        return  # Sample data already exists, no need to seed again

    user_id = add_user(db)
    add_user_settings(db, user_id)
    checking_id = add_account(db, user_id, name="Checking", type="checking", current_balance=500.0)
    savings_id = add_account(db, user_id, name="Savings", type="savings", current_balance=1000.0)


    # Create bills
    _ = add_bill(db, account_id=checking_id, name="Internet Bill", amount=60.0, start_date=datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc), recurrence="MONTHLY", notes="ISP")

    # Create transaction
    _ = add_transaction(db, account_id=checking_id, name="Sample Deposit", amount=200.0, date=datetime.datetime(2024, 1, 2, tzinfo=datetime.timezone.utc), is_recurring=False, notes="Initial deposit")

    db.close()

if __name__ == "__main__":
    wait_for_db(engine)
    Base.metadata.create_all(bind=engine)
    seed()
