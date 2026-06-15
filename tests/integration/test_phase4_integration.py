"""Integration tests for Phase 4."""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.core.database import Base
from api.domains.drought.repositories.drought_repository import DroughtRepository
from api.domains.drought.services.drought_service import DroughtService
from api.domains.soil_water.services.soil_water_service import SoilWaterService
from api.domains.financial.services.financial_service import FinancialService


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_spei_calculation():
    """Test SPEI calculation logic."""
    service = DroughtService(None)
    
    precipitation = [100, 80, 60, 40, 30, 50]
    pet = [80, 90, 100, 110, 120, 100]
    
    spei = service.calculate_spei(precipitation, pet)
    assert isinstance(spei, float)
    assert -3 <= spei <= 3


def test_rusle_calculation():
    """Test RUSLE erosion calculation."""
    service = SoilWaterService(None)
    
    # R=200, K=0.3, LS=1.5, C=0.4, P=0.6
    rusle = service.calculate_rusle(200, 0.3, 1.5, 0.4, 0.6)
    assert rusle > 0
    assert isinstance(rusle, float)


def test_npv_calculation():
    """Test NPV calculation."""
    service = FinancialService(None)
    
    npv = service.calculate_npv(
        initial_investment=100000,
        cash_flows=[30000, 35000, 40000, 45000],
        discount_rate=0.1
    )
    
    assert isinstance(npv, float)
    # NPV باید مثبت باشد با این جریان‌ها
    assert npv > 0


def test_irr_calculation():
    """Test IRR calculation."""
    service = FinancialService(None)
    
    cash_flows = [-100000, 30000, 35000, 40000, 45000]
    irr = service.calculate_irr(cash_flows)
    
    assert isinstance(irr, float)
    assert 0 < irr < 1  # IRR باید بین 0 و 100% باشد


def test_drought_severity_classification():
    """Test drought severity classification."""
    service = DroughtService(None)
    
    assert service.classify_drought_severity(-2.5) == "EXTREME_DROUGHT"
    assert service.classify_drought_severity(-1.7) == "SEVERE_DROUGHT"
    assert service.classify_drought_severity(-1.2) == "MODERATE_DROUGHT"
    assert service.classify_drought_severity(0.0) == "NORMAL"
    assert service.classify_drought_severity(1.5) == "VERY_WET"


def test_erosion_risk_classification():
    """Test erosion risk classification."""
    service = SoilWaterService(None)
    
    assert service.classify_erosion_risk(3.0) == "LOW"
    assert service.classify_erosion_risk(10.0) == "MODERATE"
    assert service.classify_erosion_risk(20.0) == "HIGH"
    assert service.classify_erosion_risk(40.0) == "VERY_HIGH"


def test_project_evaluation():
    """Test complete project evaluation."""
    service = FinancialService(None)
    
    result = service.evaluate_project(
        project_id="test_project",
        initial_investment=100000,
        cash_flows=[30000, 35000, 40000, 45000],
        discount_rate=0.1
    )
    
    assert "npv" in result
    assert "irr" in result
    assert "payback_period_years" in result
    assert "recommendation" in result
    assert result["recommendation"] in ["STRONG_INVEST", "INVEST", "CONDITIONAL_INVEST", "DO_NOT_INVEST"]
