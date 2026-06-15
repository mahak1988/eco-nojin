"""KPI Service - Business Logic for KPIs"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List, Tuple

from app.models.kpi import KPI
from app.schemas.kpi import KPICreate, KPIUpdate


async def get_kpi_by_id(db: AsyncSession, kpi_id: int) -> Optional[KPI]:
    """Get KPI by ID"""
    result = await db.execute(select(KPI).where(KPI.id == kpi_id))
    return result.scalar_one_or_none()


async def get_kpis(
    db: AsyncSession,
    project_id: Optional[int] = None,
    category: Optional[str] = None,
) -> Tuple[List[KPI], int]:
    """Get list of KPIs"""
    query = select(KPI)
    count_query = select(func.count(KPI.id))
    
    if project_id:
        query = query.where(KPI.project_id == project_id)
        count_query = count_query.where(KPI.project_id == project_id)
    if category:
        query = query.where(KPI.category == category)
        count_query = count_query.where(KPI.category == category)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    query = query.order_by(KPI.created_at.desc())
    result = await db.execute(query)
    kpis = result.scalars().all()
    
    return kpis, total


async def create_kpi(db: AsyncSession, kpi_data: KPICreate) -> KPI:
    """Create a new KPI"""
    kpi = KPI(
        name=kpi_data.name,
        description=kpi_data.description,
        value=kpi_data.value,
        target=kpi_data.target,
        unit=kpi_data.unit,
        category=kpi_data.category,
        project_id=kpi_data.project_id,
    )
    
    db.add(kpi)
    await db.commit()
    await db.refresh(kpi)
    return kpi


async def update_kpi(db: AsyncSession, kpi: KPI, kpi_data: KPIUpdate) -> KPI:
    """Update KPI"""
    update_data = kpi_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(kpi, key, value)
    
    await db.commit()
    await db.refresh(kpi)
    return kpi


async def delete_kpi(db: AsyncSession, kpi: KPI) -> None:
    """Delete KPI"""
    await db.delete(kpi)
    await db.commit()
