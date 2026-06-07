from api.services.early_warning_engine import EarlyWarningEngine
# api/modules/maintenance/router.py
from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from api.core.database import get_db
from api.modules.maintenance.models import (
    EarlyWarningAlert, MaintenanceWorkOrder, ClimateRiskScenario
)



class MaintenanceStatsResponse(BaseModel):
    """Auto-generated response model for /stats"""
    total_alerts: int = 0
    active_alerts: int = 0
    pending_work_orders: int = 0
    completed_work_orders: int = 0
    avg_response_time: float = 0.0


router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


# ============ Models ============
class AlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    title: str
    description: str
    affected_area: Optional[str]
    confidence_level: float
    detected_at: datetime
    expected_impact_at: Optional[datetime]
    is_active: bool
    acknowledged: bool
    recommended_actions: Optional[list]
    
    class Config:
        from_attributes = True


class WorkOrderResponse(BaseModel):
    id: int
    work_order_number: str
    title: str
    description: str
    work_type: Optional[str]
    priority: str
    status: str
    structure_name: Optional[str]
    location_name: Optional[str]
    created_at: datetime
    due_date: Optional[datetime]
    assigned_to: Optional[str]
    estimated_duration_hours: Optional[float]
    estimated_cost: Optional[float]
    
    class Config:
        from_attributes = True


class WorkOrderUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    completion_notes: Optional[str] = None


# ============ Endpoints ============
@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    active_only: bool = True,
    severity: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """دریافت هشدارها"""
    query = select(EarlyWarningAlert)
    
    if active_only:
        query = query.where(EarlyWarningAlert.is_active == True)
    
    if severity:
        query = query.where(EarlyWarningAlert.severity == severity)
    
    query = query.order_by(desc(EarlyWarningAlert.detected_at)).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/alerts/{alert_id}/acknowledge", response_model=Dict[str, Any])
async def acknowledge_alert(
    alert_id: int,
    acknowledged_by: str = "user",
    db: AsyncSession = Depends(get_db)
):
    """تأیید یک هشدار"""
    result = await db.execute(
        select(EarlyWarningAlert).where(EarlyWarningAlert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = True
    alert.acknowledged_by = acknowledged_by
    alert.acknowledged_at = datetime.utcnow()
    await db.commit()
    
    return {"status": "acknowledged", "alert_id": alert_id}


@router.get("/work-orders", response_model=List[WorkOrderResponse])
async def get_work_orders(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """دریافت دستور کارها"""
    query = select(MaintenanceWorkOrder)
    
    if status:
        query = query.where(MaintenanceWorkOrder.status == status)
    
    if priority:
        query = query.where(MaintenanceWorkOrder.priority == priority)
    
    query = query.order_by(
        desc(MaintenanceWorkOrder.priority == "urgent"),
        desc(MaintenanceWorkOrder.priority == "high"),
        MaintenanceWorkOrder.due_date
    ).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.put("/work-orders/{work_order_id}", response_model=Dict[str, Any])
async def update_work_order(
    work_order_id: int,
    update: WorkOrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """به‌روزرسانی دستور کار"""
    result = await db.execute(
        select(MaintenanceWorkOrder).where(MaintenanceWorkOrder.id == work_order_id)
    )
    wo = result.scalar_one_or_none()
    
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    if update.status:
        wo.status = update.status
        if update.status == "completed":
            wo.completed_at = datetime.utcnow()
    
    if update.assigned_to:
        wo.assigned_to = update.assigned_to
        wo.assigned_at = datetime.utcnow()
        wo.status = "assigned"
    
    if update.completion_notes:
        wo.completion_notes = update.completion_notes
    
    await db.commit()
    
    return {"status": "updated", "work_order_id": work_order_id}


@router.get("/stats", response_model=MaintenanceStatsResponse)
async def get_maintenance_stats(db: AsyncSession = Depends(get_db)):
    """آمار نگهداشت"""
    # تعداد هشدارهای فعال
    active_alerts = (await db.execute(
        select(func.count(EarlyWarningAlert.id)).where(EarlyWarningAlert.is_active == True)
    )).scalar() or 0
    
    # تعداد دستور کارها بر اساس وضعیت
    pending_wo = (await db.execute(
        select(func.count(MaintenanceWorkOrder.id)).where(MaintenanceWorkOrder.status == "pending")
    )).scalar() or 0
    
    in_progress_wo = (await db.execute(
        select(func.count(MaintenanceWorkOrder.id)).where(MaintenanceWorkOrder.status == "in_progress")
    )).scalar() or 0
    
    completed_wo = (await db.execute(
        select(func.count(MaintenanceWorkOrder.id)).where(MaintenanceWorkOrder.status == "completed")
    )).scalar() or 0
    
    # دستور کارهای عقب‌افتاده
    overdue_wo = (await db.execute(
        select(func.count(MaintenanceWorkOrder.id)).where(
            MaintenanceWorkOrder.due_date < datetime.utcnow(),
            MaintenanceWorkOrder.status.notin_(["completed", "cancelled"])
        )
    )).scalar() or 0
    
    return {
        "active_alerts": active_alerts,
        "pending_work_orders": pending_wo,
        "in_progress_work_orders": in_progress_wo,
        "completed_work_orders": completed_wo,
        "overdue_work_orders": overdue_wo
    }
