import pytest
from unittest.mock import MagicMock, patch

# @pytest.fixture(autouse=True)
def mock_redis():
    mock = MagicMock()
    mock.incr.return_value = 1  # Always return 1 for incr
    mock.expire.return_value = True
    with patch("app.core.rate_limit.redis_client", mock):
        yield