"""Unit tests for soil_water domain."""
import pytest
from api.domains.soil_water.services.soil_water_service import SoilWaterService
from api.domains.soil_water.repositories.soil_water_repository import SoilWaterRepository


@pytest.fixture
def soil_water_service():
    repo = SoilWaterRepository()
    return SoilWaterService(repo)


@pytest.mark.asyncio
async def test_analyze_soil_health(soil_water_service):
    """Test soil health analysis."""
    result = await soil_water_service.analyze_soil_health(
        lat=30.5,
        lon=51.5
    )
    assert "health_status" in result
    assert "recommendations" in result


@pytest.mark.asyncio
async def test_calculate_rusle(soil_water_service):
    """Test RUSLE calculation."""
    result = await soil_water_service.calculate_rusle(
        lat=30.5,
        lon=51.5
    )
    assert "rusle_value" in result
    assert "risk_level" in result
