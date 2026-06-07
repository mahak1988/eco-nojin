import pytest

from api.core.config import settings


@pytest.fixture(autouse=True)
def relax_auth_for_tests():
    """Tests run without JWT on write endpoints."""
    prev = settings.REQUIRE_AUTH_FOR_WRITES
    settings.REQUIRE_AUTH_FOR_WRITES = False
    yield
    settings.REQUIRE_AUTH_FOR_WRITES = prev
