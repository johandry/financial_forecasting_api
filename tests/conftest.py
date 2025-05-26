from unittest.mock import MagicMock, patch

import pytest

from app.core import seed
from app.core.database import Base, engine


# @pytest.fixture(autouse=True)
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
