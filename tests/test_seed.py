from app.core.seed import seed
from app.models import Account, User, UserSettings
from tests.conftest import Base, TestingSessionLocal, engine


def test_seed_creates_user_and_account_and_settings():
    db = TestingSessionLocal()

    # Delete existing tables if needed
    Base.metadata.drop_all(bind=engine)
    # Create tables for testing
    Base.metadata.create_all(bind=engine)
    # Run the seed function
    seed(db)

    user = db.query(User).filter(User.email == "johandry@example.com").first()
    assert user is not None, "User was not created by seed()"
    assert user.hashed_password is not None

    account = db.query(Account).filter(Account.user_id == user.id).first()
    assert account is not None, "Account was not created by seed()"
    assert account.name == "Checking"

    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    assert settings is not None, "UserSettings was not created by seed()"
    assert settings.buffer_amount == 50.0

    db.close()
