import datetime

from app.models import Account, User, UserSettings


def add_user(db):
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


def add_user_settings(db, user_id):
    settings = UserSettings(
        user_id=user_id, buffer_amount=50.0, forecast_horizon_months=3
    )
    db.add(settings)
    db.commit()
    db.refresh(settings)


def add_account(
    db,
    user_id: int,
    name: str = "Checking",
    type: str = "checking",
    current_balance: float = 0.0,
):
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


def get_or_create_user(db) -> int:
    user = db.query(User).filter_by(email="johandry@example.com").first()
    if not user:
        return add_user(db)
    return user.id


def get_or_create_account(db) -> int:
    account = db.query(Account).filter_by(id=1).first()
    if not account:
        user_id = get_or_create_user(db)
        return add_account(db, user_id)
    return account.id


def get_or_create_user_settings(db):
    user_id = get_or_create_user(db)
    settings = db.query(UserSettings).filter_by(user_id=user_id).first()
    if not settings:
        add_user_settings(db, user_id)
    return user_id
