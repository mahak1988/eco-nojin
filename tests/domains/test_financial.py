"""Unit tests for financial domain."""
import pytest
from api.domains.financial.services.financial_service import FinancialService
from api.domains.financial.repositories.financial_repository import FinancialRepository


@pytest.fixture
def financial_service():
    repo = FinancialRepository()
    return FinancialService(repo)


@pytest.mark.asyncio
async def test_calculate_npv(financial_service):
    """Test NPV calculation."""
    npv = await financial_service.calculate_npv(
        initial_investment=100000,
        annual_cash_flows=[30000, 35000, 40000, 45000],
        discount_rate=0.1
    )
    assert isinstance(npv, float)


@pytest.mark.asyncio
async def test_evaluate_project(financial_service):
    """Test project evaluation."""
    result = await financial_service.evaluate_project("project_001")
    assert "npv" in result
    assert "irr" in result
    assert "recommendation" in result
