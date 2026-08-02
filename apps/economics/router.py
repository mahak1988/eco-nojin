"""
Economics Router
================
FastAPI router for economic analysis endpoints.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from apps.economics.schemas import (
    EconomicAnalysisCreate,
    EconomicAnalysisUpdate,
    EconomicAnalysisResponse,
    EconomicAnalysisListResponse,
    CostBenefitResult,
)
from apps.economics.service import EconomicsService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/economics",
    tags=["economics"],
)


def get_service(session: AsyncSession = Depends()) -> EconomicsService:
    """Get EconomicsService instance."""
    return EconomicsService(session)


@router.get("/analyses", response_model=EconomicAnalysisListResponse)
async def list_analyses(
    skip: int = 0,
    limit: int = 100,
    service: EconomicsService = Depends(get_service),
) -> EconomicAnalysisListResponse:
    """List economic analyses with pagination."""
    items, total = await service.list(skip=skip, limit=limit)
    return EconomicAnalysisListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/analyses/{analysis_id}", response_model=EconomicAnalysisResponse)
async def get_analysis(
    analysis_id: int,
    service: EconomicsService = Depends(get_service),
) -> EconomicAnalysisResponse:
    """Get a single economic analysis by ID."""
    analysis = await service.get(analysis_id)
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return analysis


@router.post("/analyses", response_model=EconomicAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    data: EconomicAnalysisCreate,
    service: EconomicsService = Depends(get_service),
) -> EconomicAnalysisResponse:
    """Create a new economic analysis."""
    analysis = await service.create(data)
    return analysis


@router.patch("/analyses/{analysis_id}", response_model=EconomicAnalysisResponse)
async def update_analysis(
    analysis_id: int,
    data: EconomicAnalysisUpdate,
    service: EconomicsService = Depends(get_service),
) -> EconomicAnalysisResponse:
    """Update an existing economic analysis."""
    analysis = await service.update(analysis_id, data)
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return analysis


@router.delete("/analyses/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: int,
    service: EconomicsService = Depends(get_service),
) -> None:
    """Delete an economic analysis."""
    deleted = await service.delete(analysis_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")


@router.post("/cost-benefit", response_model=CostBenefitResult)
async def cost_benefit_calculation(
    total_cost: float,
    total_benefit: float,
    discount_rate: float = 0.1,
    time_horizon_years: int = 5,
) -> CostBenefitResult:
    """Perform a standalone cost-benefit calculation without storing."""
    return EconomicsService.calculate_cost_benefit(
        total_cost=total_cost,
        total_benefit=total_benefit,
        discount_rate=discount_rate,
        time_horizon=time_horizon_years,
    )


@router.post("/npv", response_model=dict)
async def npv_calculation(
    initial_investment: float,
    annual_cash_flows: list[float],
    discount_rate: float,
) -> dict:
    """Calculate NPV from cash flows."""
    npv = EconomicsService.calculate_npv(
        initial_investment=initial_investment,
        annual_cash_flows=annual_cash_flows,
        discount_rate=discount_rate,
    )
    return {"npv": npv}


@router.post("/irr", response_model=dict)
async def irr_calculation(
    initial_investment: float,
    annual_cash_flows: list[float],
) -> dict:
    """Calculate IRR from cash flows."""
    irr = EconomicsService.calculate_irr(
        initial_investment=initial_investment,
        annual_cash_flows=annual_cash_flows,
    )
    return {"irr": irr}
