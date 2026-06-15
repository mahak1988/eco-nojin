"""Unit tests for drought domain."""
import pytest
from datetime import datetime
from api.domains.drought.services.drought_service import DroughtService
from api.domains.drought.repositories.drought_repository import DroughtRepository


@pytest.fixture
def drought_service():
    repo = DroughtRepository()
    return DroughtService(repo)


@pytest.mark.asyncio
async def test_calculate_drought_severity(drought_service):
    """Test drought severity calculation."""
    severity = await drought_service.calculate_drought_severity(
        lat=30.5,
        lon=51.5,
        date=datetime.now()
    )
    assert severity in ["NORMAL", "MILD_DROUGHT", "MODERATE_DROUGHT", 
                        "SEVERE_DROUGHT", "EXTREME_DROUGHT", "NO_DATA"]


@pytest.mark.asyncio
async def test_get_early_warning(drought_service):
    """Test early warning system."""
    warning = await drought_service.get_early_warning(
        region_lat=30.5,
        region_lon=51.5
    )
    assert "severity" in warning
    assert "recommendation" in warning
