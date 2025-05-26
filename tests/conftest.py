from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

# Use SQLite file database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def mock_redis():
    mock = MagicMock()
    mock.incr.return_value = 1  # Always return 1 for incr
    mock.expire.return_value = True
    with patch("app.core.rate_limit.redis_client", mock):
        yield


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    # Delete existing tables if needed
    Base.metadata.drop_all(bind=engine)
    # Create tables for testing
    Base.metadata.create_all(bind=engine)
    yield
    # Optionally, drop tables after tests:
    # Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    # Drop and recreate all tables before each test function
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
