"""
Economics Service
=================
Business logic layer for economic analysis operations.
Calculates NPV, IRR, ROI, payback period, and break-even point.
"""

from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.economics.models import BenefitItem, CostItem, EconomicAnalysis
from apps.economics.schemas import (
    CostBenefitResult,
    EconomicAnalysisCreate,
    EconomicAnalysisUpdate,
)

logger = logging.getLogger(__name__)


class EconomicsService:
    """Service for economic analysis operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, analysis_id: int) -> EconomicAnalysis | None:
        """Get a single analysis by ID."""
        result = await self.session.execute(
            select(EconomicAnalysis).where(EconomicAnalysis.id == analysis_id)
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[list[EconomicAnalysis], int]:
        """List analyses with pagination."""
        limit = min(limit, 1000)
        result = await self.session.execute(
            select(EconomicAnalysis).order_by(EconomicAnalysis.id.desc()).offset(skip).limit(limit)
        )
        items = list(result.scalars().all())

        count_result = await self.session.execute(
            select(func.count()).select_from(EconomicAnalysis)
        )
        total = count_result.scalar_one()
        return items, total

    async def create(self, data: EconomicAnalysisCreate) -> EconomicAnalysis:
        """Create a new economic analysis with cost and benefit items."""
        analysis = EconomicAnalysis(
            farm_id=data.farm_id,
            project_id=data.project_id,
            title=data.title,
            analysis_type=data.analysis_type,
            currency=data.currency,
            discount_rate=data.discount_rate,
            time_horizon_years=data.time_horizon_years,
            notes=data.notes,
        )

        # Add cost items
        total_cost = 0.0
        for ci in data.cost_items:
            item = CostItem(
                category=ci.category,
                description=ci.description,
                amount=ci.amount,
                is_recurring=ci.is_recurring,
                frequency=ci.frequency,
                year=ci.year,
            )
            analysis.cost_items.append(item)
            total_cost += ci.amount

        # Add benefit items
        total_benefit = 0.0
        for bi in data.benefit_items:
            item = BenefitItem(
                category=bi.category,
                description=bi.description,
                amount=bi.amount,
                is_recurring=bi.is_recurring,
                frequency=bi.frequency,
                year=bi.year,
            )
            analysis.benefit_items.append(item)
            total_benefit += bi.amount

        analysis.total_cost = total_cost
        analysis.total_revenue = total_benefit
        analysis.total_benefit = total_benefit

        # Calculate financial metrics
        result = self.calculate_cost_benefit(
            total_cost=total_cost,
            total_benefit=total_benefit,
            discount_rate=analysis.discount_rate,
            time_horizon=analysis.time_horizon_years,
        )
        analysis.npv = result.npv
        analysis.roi = result.roi
        analysis.payback_period_years = result.payback_period_years
        analysis.break_even_point = result.break_even_point

        self.session.add(analysis)
        await self.session.flush()
        await self.session.refresh(analysis)
        return analysis

    async def update(
        self, analysis_id: int, data: EconomicAnalysisUpdate
    ) -> EconomicAnalysis | None:
        """Update an existing analysis."""
        analysis = await self.get(analysis_id)
        if not analysis:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(analysis, key, value)
        await self.session.flush()
        await self.session.refresh(analysis)
        return analysis

    async def delete(self, analysis_id: int) -> bool:
        """Delete an analysis. Returns True if deleted."""
        analysis = await self.get(analysis_id)
        if not analysis:
            return False
        await self.session.delete(analysis)
        await self.session.flush()
        return True

    @staticmethod
    def calculate_cost_benefit(
        total_cost: float,
        total_benefit: float,
        discount_rate: float = 0.1,
        time_horizon: int = 5,
    ) -> CostBenefitResult:
        """
        Calculate cost-benefit analysis metrics.

        Args:
            total_cost: Total cost amount
            total_benefit: Total benefit amount
            discount_rate: Annual discount rate (0-1)
            time_horizon: Number of years for analysis

        Returns:
            CostBenefitResult with all calculated metrics
        """
        net_benefit = total_benefit - total_cost
        benefit_cost_ratio = total_benefit / total_cost if total_cost > 0 else 0.0
        roi = (net_benefit / total_cost * 100) if total_cost > 0 else 0.0

        # NPV: assume benefits spread evenly over time horizon
        if total_benefit > 0 and time_horizon > 0:
            annual_benefit = total_benefit / time_horizon
            npv = -total_cost
            for year in range(1, time_horizon + 1):
                npv += annual_benefit / ((1 + discount_rate) ** year)
        else:
            npv = net_benefit

        # Payback period (simple)
        if total_benefit > 0 and time_horizon > 0:
            annual_benefit = total_benefit / time_horizon
            payback = total_cost / annual_benefit if annual_benefit > 0 else None
        else:
            payback = None

        # Break-even point (in currency units)
        break_even = total_cost if total_cost > 0 else None

        return CostBenefitResult(
            total_cost=total_cost,
            total_benefit=total_benefit,
            net_benefit=net_benefit,
            benefit_cost_ratio=round(benefit_cost_ratio, 4),
            roi=round(roi, 2),
            npv=round(npv, 2) if npv is not None else None,
            payback_period_years=round(payback, 2) if payback is not None else None,
            break_even_point=break_even,
        )

    @staticmethod
    def calculate_npv(
        initial_investment: float,
        annual_cash_flows: list[float],
        discount_rate: float,
    ) -> float:
        """
        Calculate Net Present Value.

        Args:
            initial_investment: Initial cost (negative cash flow)
            annual_cash_flows: List of annual cash flows
            discount_rate: Discount rate (0-1)

        Returns:
            NPV value
        """
        npv = -initial_investment
        for year, cf in enumerate(annual_cash_flows, start=1):
            npv += cf / ((1 + discount_rate) ** year)
        return round(npv, 2)

    @staticmethod
    def calculate_irr(
        initial_investment: float,
        annual_cash_flows: list[float],
        max_iterations: int = 100,
        tolerance: float = 1e-6,
    ) -> float | None:
        """
        Calculate Internal Rate of Return using Newton-Raphson method.

        Args:
            initial_investment: Initial cost
            annual_cash_flows: List of annual cash flows
            max_iterations: Maximum iterations for convergence
            tolerance: Convergence tolerance

        Returns:
            IRR as a percentage, or None if no convergence
        """
        if not annual_cash_flows:
            return None

        # Initial guess
        rate = 0.1

        for _ in range(max_iterations):
            npv = -initial_investment
            dnpv = 0.0
            for year, cf in enumerate(annual_cash_flows, start=1):
                factor = (1 + rate) ** year
                npv += cf / factor
                dnpv -= year * cf / (factor * (1 + rate))

            if abs(dnpv) < tolerance:
                return None

            new_rate = rate - npv / dnpv
            if abs(new_rate - rate) < tolerance:
                return round(new_rate * 100, 2)
            rate = new_rate

            if rate < -0.99:
                return None

        return None
