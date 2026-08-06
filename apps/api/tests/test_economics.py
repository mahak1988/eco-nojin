"""
Economics Module Tests
======================
Tests for EconomicsService cost-benefit, NPV, and IRR calculations.
"""

import pytest

from apps.economics.service import EconomicsService


class TestCostBenefit:
    """Tests for cost-benefit calculation methods."""

    def test_cost_benefit_positive(self) -> None:
        """Verify positive net benefit calculation."""
        result = EconomicsService.calculate_cost_benefit(
            total_cost=1000.0,
            total_benefit=2000.0,
            discount_rate=0.1,
            time_horizon=5,
        )
        assert result.total_cost == 1000.0
        assert result.total_benefit == 2000.0
        assert result.net_benefit == 1000.0
        assert result.benefit_cost_ratio == 2.0
        assert result.roi == 100.0

    def test_cost_benefit_zero_cost(self) -> None:
        """Verify zero-cost scenario doesn't crash."""
        result = EconomicsService.calculate_cost_benefit(
            total_cost=0.0,
            total_benefit=500.0,
            discount_rate=0.1,
            time_horizon=5,
        )
        assert result.net_benefit == 500.0
        assert result.benefit_cost_ratio == 0.0
        assert result.roi == 0.0

    def test_cost_benefit_negative(self) -> None:
        """Verify negative net benefit (costs exceed benefits)."""
        result = EconomicsService.calculate_cost_benefit(
            total_cost=3000.0,
            total_benefit=1000.0,
            discount_rate=0.1,
            time_horizon=5,
        )
        assert result.net_benefit == -2000.0
        assert result.benefit_cost_ratio == pytest.approx(0.3333, abs=0.001)
        assert result.roi == pytest.approx(-66.67, abs=0.01)


class TestNPV:
    """Tests for NPV calculation."""

    def test_npv_simple(self) -> None:
        """Verify simple NPV calculation."""
        npv = EconomicsService.calculate_npv(
            initial_investment=1000.0,
            annual_cash_flows=[500.0, 500.0, 500.0],
            discount_rate=0.1,
        )
        expected = -1000.0
        for year in range(1, 4):
            expected += 500.0 / ((1 + 0.1) ** year)
        assert npv == round(expected, 2)

    def test_npv_zero_investment(self) -> None:
        """Verify NPV with zero initial investment."""
        npv = EconomicsService.calculate_npv(
            initial_investment=0.0,
            annual_cash_flows=[100.0],
            discount_rate=0.1,
        )
        assert npv == round(100.0 / 1.1, 2)

    def test_npv_no_cash_flows(self) -> None:
        """Verify NPV with empty cash flows."""
        npv = EconomicsService.calculate_npv(
            initial_investment=1000.0,
            annual_cash_flows=[],
            discount_rate=0.1,
        )
        assert npv == -1000.0


class TestIRR:
    """Tests for IRR calculation."""

    def test_irr_simple(self) -> None:
        """Verify IRR for a simple project."""
        irr = EconomicsService.calculate_irr(
            initial_investment=1000.0,
            annual_cash_flows=[500.0, 500.0, 500.0],
        )
        assert irr is not None
        assert irr > 0

    def test_irr_no_cash_flows(self) -> None:
        """Verify IRR returns None for empty cash flows."""
        irr = EconomicsService.calculate_irr(
            initial_investment=1000.0,
            annual_cash_flows=[],
        )
        assert irr is None

    def test_irr_breakeven(self) -> None:
        """Verify IRR for a project that exactly breaks even."""
        # If cash flows equal investment, IRR should be high
        irr = EconomicsService.calculate_irr(
            initial_investment=300.0,
            annual_cash_flows=[100.0, 100.0, 100.0],
        )
        # NPV=0 at IRR; roughly 0% since 3 years of 100 = 300
        assert irr is not None


class TestCostBenefitResult:
    """Tests for CostBenefitResult model."""

    def test_result_fields(self) -> None:
        """Verify CostBenefitResult has all expected fields."""
        from apps.economics.schemas import CostBenefitResult

        result = CostBenefitResult(
            total_cost=1000.0,
            total_benefit=2000.0,
            net_benefit=1000.0,
            benefit_cost_ratio=2.0,
            roi=100.0,
        )
        assert result.total_cost == 1000.0
        assert result.total_benefit == 2000.0
        assert result.net_benefit == 1000.0
        assert result.benefit_cost_ratio == 2.0
        assert result.roi == 100.0


class TestEconomicModels:
    """Tests for Economics model definitions."""

    def test_models_importable(self) -> None:
        """Verify economics models are importable."""
        from apps.economics.models import EconomicAnalysis, CostItem, BenefitItem
        from apps.economics.models import AnalysisType, Currency

        assert EconomicAnalysis is not None
        assert CostItem is not None
        assert BenefitItem is not None
        assert AnalysisType.COST_BENEFIT == "cost_benefit"
        assert Currency.USD == "USD"

    def test_analysis_model_definition(self) -> None:
        """Verify EconomicAnalysis model has expected fields."""
        from apps.economics.models import EconomicAnalysis

        # Use SQLAlchemy inspection
        column_names = {c.name for c in EconomicAnalysis.__table__.columns}
        expected = {
            "id", "farm_id", "project_id", "title", "analysis_type",
            "currency", "total_cost", "total_revenue", "total_benefit",
            "npv", "irr", "roi", "payback_period_years", "break_even_point",
            "discount_rate", "time_horizon_years", "notes", "is_active",
            "created_at", "updated_at",
        }
        assert expected.issubset(column_names)
