"""Unit tests for psychology domain."""
import pytest
from api.domains.psychology.services.psychology_service import PsychologyService
from api.domains.psychology.repositories.psychology_repository import PsychologyRepository


@pytest.fixture
def psychology_service():
    repo = PsychologyRepository()
    return PsychologyService(repo)


@pytest.mark.asyncio
async def test_score_test(psychology_service):
    """Test scoring."""
    score = await psychology_service.score_test(
        test_id="test_001",
        answers=[3, 4, 5, 2, 4]
    )
    assert 0 <= score <= 10


@pytest.mark.asyncio
async def test_submit_test(psychology_service):
    """Test submission."""
    result = await psychology_service.submit_test(
        user_id="user_001",
        test_id="test_001",
        answers=[3, 4, 5, 2, 4]
    )
    assert "score" in result
    assert "interpretation" in result
    assert "recommendations" in result
