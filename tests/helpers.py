from app.core import seed
from app.models import Account, User, UserSettings


def get_or_create_user(db) -> int:
    user = db.query(User).filter_by(email="johandry@example.com").first()
    if not user:
        return seed.add_user(db)
    return user.id


def get_or_create_account(db) -> int:
    account = db.query(Account).filter_by(id=1).first()
    if not account:
        user_id = get_or_create_user(db)
        return seed.add_account(db, user_id)
    return account.id


def get_or_create_user_settings(db):
    user_id = get_or_create_user(db)
    settings = db.query(UserSettings).filter_by(user_id=user_id).first()
    if not settings:
        seed.add_user_settings(db, user_id)
    return user_id
