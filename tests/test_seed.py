import yaml
from app.core.seed import seed_database
from app.models import Account, User, UserSettings
from tests.conftest import Base, TestingSessionLocal, engine


def test_seed_creates_user_and_account_and_settings():
    db = TestingSessionLocal()

    # Delete existing tables if needed
    Base.metadata.drop_all(bind=engine)
    # Create tables for testing
    Base.metadata.create_all(bind=engine)

    # YAML content as a multiline string
    yaml_content = """
    users:
      - email: johandry@example.com
        password: johandrypass

    user_settings:
      - user_email: johandry@example.com
        buffer_amount: 50.0
        forecast_horizon_months: 3

    accounts:
      - user_email: johandry@example.com
        name: Checking
        current_balance: 500.0
      - user_email: johandry@example.com
        name: Savings
        current_balance: 1_000.0

    bills:
      - account_name: Checking
        name: Rent
        amount: 1200.0
        start_date: "2025-01-01"
        recurrence: monthly
      - account_name: Checking
        name: Internet Bill
        amount: 60.0
        start_date: "2025-01-01"
        recurrence: monthly

    transactions:
      - account_name: Checking
        name: Paycheck
        amount: 2000.0
        date: "2025-01-02"
        type: credit
    """

    # Convert YAML string to Python dictionary
    data = yaml.safe_load(yaml_content)

    # Run the seed function with the YAML data
    seed_database(db, data)

    # Assertions
    user = db.query(User).filter(User.email == "johandry@example.com").first()
    assert user is not None, "User was not created by seed_database()"
    assert user.hashed_password is not None

    account = db.query(Account).filter(Account.user_id == user.id).first()
    assert account is not None, "Account was not created by seed_database()"
    assert account.name == "Checking"

    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    assert settings is not None, "UserSettings was not created by seed_database()"
    assert settings.buffer_amount == 50.0

    db.close()
