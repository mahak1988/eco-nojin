"""KPIs Endpoints - Full CRUD"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.schemas.kpi import KPICreate, KPIUpdate, KPIResponse, KPIListResponse
from app.services.kpi_service import (
    get_kpi_by_id, get_kpis, create_kpi, update_kpi, delete_kpi,
)


router = APIRouter()


@router.post("/", response_model=KPIResponse, status_code=status.HTTP_201_CREATED)
async def create_kpi_endpoint(
    kpi_data: KPICreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(["admin", "researcher"])),
):
    """Create a new KPI"""
    kpi = await create_kpi(db, kpi_data)
    return kpi


@router.get("/", response_model=KPIListResponse)
async def list_kpis(
    project_id: Optional[int] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """List KPIs with filters"""
    kpis, total = await get_kpis(db, project_id=project_id, category=category)
    return KPIListResponse(kpis=kpis, total=total)


@router.get("/{kpi_id}", response_model=KPIResponse)
async def get_kpi(
    kpi_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Get KPI by ID"""
    kpi = await get_kpi_by_id(db, kpi_id)
    if not kpi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KPI not found",
        )
    return kpi


@router.patch("/{kpi_id}", response_model=KPIResponse)
async def update_kpi_endpoint(
    kpi_id: int,
    kpi_data: KPIUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(["admin", "researcher"])),
):
    """Update KPI"""
    kpi = await get_kpi_by_id(db, kpi_id)
    if not kpi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KPI not found",
        )
    return await update_kpi(db, kpi, kpi_data)


@router.delete("/{kpi_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kpi_endpoint(
    kpi_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(["admin"])),
):
    """Delete KPI (admin only)"""
    kpi = await get_kpi_by_id(db, kpi_id)
    if not kpi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KPI not found",
        )
    await delete_kpi(db, kpi)
