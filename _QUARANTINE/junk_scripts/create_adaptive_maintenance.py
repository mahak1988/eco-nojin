#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ لایه 3: نگهداشت تطبیقی و مدیریت ریسک
- سیستم هشدار زودهنگام هیبریدی (Hybrid EWS)
- موتور تولید دستور کار نگهداری
- داشبورد مدیریت نگهداشت
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


# ========== 1. بک‌اند: مدل‌های دیتابیس ==========
def create_maintenance_models():
    print("\n🗄️ ایجاد مدل‌های نگهداشت...")
    
    content = '''# api/modules/maintenance/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Index, JSON, Boolean, Enum
from sqlalchemy.sql import func
from api.core.database import Base
import enum


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class WorkOrderStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkOrderPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class EarlyWarningAlert(Base):
    """هشدارهای سیستم هشدار زودهنگام"""
    __tablename__ = "early_warning_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)  # flood, drought, structure_damage, etc.
    severity = Column(String(20), nullable=False)  # info, warning, critical, emergency
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    affected_area = Column(String(200))  # منطقه تحت تأثیر
    latitude = Column(Float)
    longitude = Column(Float)
    
    # داده‌های ورودی
    trigger_data = Column(JSON)  # داده‌هایی که باعث فعال‌سازی شدند
    confidence_level = Column(Float, default=0.8)  # سطح اطمینان پیش‌بینی
    
    # زمان‌بندی
    detected_at = Column(DateTime, server_default=func.now())
    expected_impact_at = Column(DateTime)  # زمان پیش‌بینی‌شده تأثیر
    expires_at = Column(DateTime)
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime)
    
    # اقدامات
    recommended_actions = Column(JSON)  # اقدامات پیشنهادی
    auto_generated_work_orders = Column(JSON, default=[])  # IDs of work orders


class MaintenanceWorkOrder(Base):
    """دستور کارهای نگهداری"""
    __tablename__ = "maintenance_work_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_number = Column(String(50), unique=True, nullable=False)
    
    # اطلاعات اصلی
    title = Column(String(200), nullable=False)
    description = Column(String(2000))
    work_type = Column(String(50))  # inspection, repair, cleaning, replacement
    priority = Column(String(20), nullable=False)  # low, medium, high, urgent
    
    # محل
    structure_id = Column(Integer)  # ارتباط با سازه
    structure_name = Column(String(100))
    location_name = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # زمان‌بندی
    created_at = Column(DateTime, server_default=func.now())
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    
    # مسئولین
    created_by = Column(String(100))  # auto یا user
    assigned_to = Column(String(100))
    assigned_at = Column(DateTime)
    
    # وضعیت
    status = Column(String(20), default="pending")  # pending, assigned, in_progress, completed, cancelled
    
    # ارتباط با هشدار
    alert_id = Column(Integer, nullable=True)  # ارتباط با EarlyWarningAlert
    
    # جزئیات فنی
    required_tools = Column(JSON)  # ابزارهای مورد نیاز
    required_materials = Column(JSON)  # مواد مورد نیاز
    estimated_duration_hours = Column(Float)
    estimated_cost = Column(Float)
    
    # گزارش تکمیل
    completion_notes = Column(String(2000))
    completion_photos = Column(JSON)  # URLs of photos
    actual_duration_hours = Column(Float)
    actual_cost = Column(Float)


class ClimateRiskScenario(Base):
    """سناریوهای ریسک اقلیمی"""
    __tablename__ = "climate_risk_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_name = Column(String(200), nullable=False)
    scenario_type = Column(String(50))  # drought, flood, extreme_heat, etc.
    
    # پارامترهای سناریو
    parameters = Column(JSON)  # duration, intensity, return_period, etc.
    
    # تأثیرات پیش‌بینی‌شده
    affected_structures = Column(JSON)  # list of structure IDs
    estimated_damage = Column(JSON)  # damage assessment
    economic_loss = Column(Float)  # estimated loss in currency
    
    # اقدامات پیشنهادی
    mitigation_actions = Column(JSON)
    adaptation_strategies = Column(JSON)
    
    # زمان‌بندی
    created_at = Column(DateTime, server_default=func.now())
    simulation_date = Column(DateTime)


# Indexes
Index("idx_alert_severity", EarlyWarningAlert.severity, EarlyWarningAlert.is_active)
Index("idx_alert_time", EarlyWarningAlert.detected_at.desc())
Index("idx_wo_status", MaintenanceWorkOrder.status, MaintenanceWorkOrder.priority)
Index("idx_wo_due", MaintenanceWorkOrder.due_date)
'''
    
    write_file(API_DIR / "modules" / "maintenance" / "models.py", content)


# ========== 2. بک‌اند: موتور هشدار زودهنگام ==========
def create_ews_engine():
    print("\n🚨 ایجاد موتور هشدار زودهنگام...")
    
    content = '''# api/services/early_warning_engine.py
"""
سیستم هشدار زودهنگام هیبریدی (Hybrid Early Warning System)
ترکیب داده‌های IoT، ماهواره‌ای و پیش‌بینی‌های هواشناسی
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import async_session
from api.modules.iot.models import SensorReading, Sensor
from api.modules.maintenance.models import EarlyWarningAlert, MaintenanceWorkOrder

logger = logging.getLogger(__name__)


class EarlyWarningEngine:
    """موتور هشدار زودهنگام هیبریدی"""
    
    def __init__(self):
        self.running = False
        self.check_interval = 300  # 5 minutes
    
    async def start(self):
        """شروع پایش مداوم"""
        self.running = True
        logger.info("🚨 Early Warning Engine started")
        
        while self.running:
            try:
                await self._check_all_alerts()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ EWS error: {e}")
                await asyncio.sleep(60)
    
    async def _check_all_alerts(self):
        """بررسی تمام شرایط هشدار"""
        async with async_session() as session:
            # 1. بررسی هشدارهای سیلاب
            await self._check_flood_risk(session)
            
            # 2. بررسی هشدارهای خشکسالی
            await self._check_drought_risk(session)
            
            # 3. بررسی خرابی سازه‌ها
            await self._check_structure_damage(session)
            
            # 4. بررسی تنش آبی
            await self._check_water_stress(session)
            
            await session.commit()
    
    async def _check_flood_risk(self, session: AsyncSession):
        """بررسی ریسک سیلاب"""
        # دریافت آخرین خوانش باران‌سنج‌ها
        query = (
            select(SensorReading)
            .where(SensorReading.sensor_code.like('RAIN-%'))
            .order_by(SensorReading.timestamp.desc())
            .limit(10)
        )
        result = await session.execute(query)
        rain_readings = result.scalars().all()
        
        for reading in rain_readings:
            if reading.value and reading.value > 50:  # > 50mm/hr
                # ایجاد هشدار
                alert = EarlyWarningAlert(
                    alert_type="flood",
                    severity="critical" if reading.value > 100 else "warning",
                    title=f"هشدار سیلاب - بارش شدید {reading.value}mm/hr",
                    description=f"بارش شدید با شدت {reading.value} میلی‌متر بر ساعت detected. احتمال سیلاب در 2-6 ساعت آینده.",
                    affected_area="حوضه آبریز پایین‌دست",
                    trigger_data={
                        "sensor_code": reading.sensor_code,
                        "rainfall_mm_hr": reading.value,
                        "timestamp": reading.timestamp.isoformat()
                    },
                    confidence_level=0.85,
                    expected_impact_at=datetime.utcnow() + timedelta(hours=3),
                    expires_at=datetime.utcnow() + timedelta(hours=12),
                    recommended_actions=[
                        "تخلیه مناطق低洼",
                        "باز کردن مسیرهای آب",
                        "آماده‌باش تیم‌های امداد",
                        "هشدار به کشاورزان پایین‌دست"
                    ]
                )
                session.add(alert)
                logger.warning(f"🌊 Flood alert generated: {reading.value}mm/hr")
                
                # تولید خودکار دستور کار
                await self._generate_flood_work_order(session, alert)
    
    async def _check_drought_risk(self, session: AsyncSession):
        """بررسی ریسک خشکسالی"""
        # دریافت میانگین رطوبت خاک 7 روز اخیر
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        query = (
            select(SensorReading)
            .where(
                SensorReading.sensor_code.like('TDR-%'),
                SensorReading.timestamp >= seven_days_ago
            )
        )
        result = await session.execute(query)
        moisture_readings = result.scalars().all()
        
        if moisture_readings:
            avg_moisture = sum(r.value for r in moisture_readings if r.value) / len(moisture_readings)
            
            if avg_moisture < 15:  # رطوبت خیلی کم
                alert = EarlyWarningAlert(
                    alert_type="drought",
                    severity="warning" if avg_moisture < 15 else "critical",
                    title=f"هشدار خشکسالی - رطوبت خاک {avg_moisture:.1f}%",
                    description=f"میانگین رطوبت خاک در 7 روز اخیر {avg_moisture:.1f}% بوده که نشان‌دهنده تنش آبی شدید است.",
                    affected_area="مناطق کشاورزی",
                    trigger_data={
                        "avg_moisture_percent": avg_moisture,
                        "period_days": 7,
                        "sensor_count": len(moisture_readings)
                    },
                    confidence_level=0.75,
                    expected_impact_at=datetime.utcnow() + timedelta(days=14),
                    expires_at=datetime.utcnow() + timedelta(days=30),
                    recommended_actions=[
                        "کاهش آبیاری غیرضروری",
                        "استفاده از روش‌های حفظ رطوبت",
                        "تغییر الگوی کشت",
                        "فعال‌سازی منابع آب جایگزین"
                    ]
                )
                session.add(alert)
                logger.warning(f"🏜️ Drought alert: moisture {avg_moisture:.1f}%")
    
    async def _check_structure_damage(self, session: AsyncSession):
        """بررسی خرابی سازه‌ها"""
        # بررسی تغییرات ناگهانی در داده‌های فلوم‌ها
        query = (
            select(SensorReading)
            .where(SensorReading.sensor_code.like('FLUME-%'))
            .order_by(SensorReading.timestamp.desc())
            .limit(20)
        )
        result = await session.execute(query)
        flume_readings = result.scalars().all()
        
        # بررسی نوسانات شدید
        if len(flume_readings) >= 2:
            recent = [r.value for r in flume_readings[:5] if r.value]
            older = [r.value for r in flume_readings[5:10] if r.value]
            
            if recent and older:
                avg_recent = sum(recent) / len(recent)
                avg_older = sum(older) / len(older)
                
                change_percent = abs(avg_recent - avg_older) / avg_older * 100
                
                if change_percent > 50:  # تغییر بیش از 50%
                    alert = EarlyWarningAlert(
                        alert_type="structure_damage",
                        severity="critical",
                        title=f"احتمال خرابی سازه - تغییر {change_percent:.0f}% در دبی",
                        description=f"تغییر ناگهانی {change_percent:.0f}% در دبی اندازه‌گیری شده. احتمال گرفتگی یا خرابی سازه.",
                        affected_area="سازه‌های آبخیزداری",
                        trigger_data={
                            "change_percent": change_percent,
                            "recent_avg": avg_recent,
                            "older_avg": avg_older
                        },
                        confidence_level=0.70,
                        expected_impact_at=datetime.utcnow() + timedelta(hours=6),
                        expires_at=datetime.utcnow() + timedelta(hours=24),
                        recommended_actions=[
                            "بازرسی فوری سازه",
                            "بررسی گرفتگی احتمالی",
                            "آماده‌سازی تجهیزات تعمیر",
                            "تخلیه احتیاطی آب بالا‌دست"
                        ]
                    )
                    session.add(alert)
                    logger.warning(f"🏗️ Structure damage alert: {change_percent:.0f}% change")
                    
                    # تولید خودکار دستور کار بازرسی
                    await self._generate_inspection_work_order(session, alert)
    
    async def _check_water_stress(self, session: AsyncSession):
        """بررسی تنش آبی"""
        # مقایسه دبی ورودی و خروجی
        inflow_query = (
            select(SensorReading)
            .where(SensorReading.sensor_code == 'FLUME-001')
            .order_by(SensorReading.timestamp.desc())
            .limit(1)
        )
        outflow_query = (
            select(SensorReading)
            .where(SensorReading.sensor_code == 'FLUME-002')
            .order_by(SensorReading.timestamp.desc())
            .limit(1)
        )
        
        inflow_result = await session.execute(inflow_query)
        outflow_result = await session.execute(outflow_query)
        
        inflow = inflow_result.scalar_one_or_none()
        outflow = outflow_result.scalar_one_or_none()
        
        if inflow and outflow and inflow.value and outflow.value:
            loss_percent = (inflow.value - outflow.value) / inflow.value * 100
            
            if loss_percent > 30:  # تلفات بیش از 30%
                alert = EarlyWarningAlert(
                    alert_type="water_stress",
                    severity="warning",
                    title=f"تنش آبی - تلفات {loss_percent:.0f}%",
                    description=f"تلفات آب بین ورودی و خروجی {loss_percent:.0f}% است که نشان‌دهنده نشت یا تبخیر شدید است.",
                    affected_area="شبکه آبرسانی",
                    trigger_data={
                        "inflow_m3s": inflow.value,
                        "outflow_m3s": outflow.value,
                        "loss_percent": loss_percent
                    },
                    confidence_level=0.80,
                    expected_impact_at=datetime.utcnow() + timedelta(days=7),
                    expires_at=datetime.utcnow() + timedelta(days=14),
                    recommended_actions=[
                        "بررسی نشتی احتمالی",
                        "عایق‌بندی کانال‌ها",
                        "بهینه‌سازی مصرف",
                        "تعمیرات فوری"
                    ]
                )
                session.add(alert)
                logger.warning(f"💧 Water stress alert: {loss_percent:.0f}% loss")
    
    async def _generate_flood_work_order(self, session: AsyncSession, alert: EarlyWarningAlert):
        """تولید خودکار دستور کار برای سیلاب"""
        work_order = MaintenanceWorkOrder(
            work_order_number=f"WO-FLOOD-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            title="اقدامات فوری پیشگیری از سیلاب",
            description=f"هشدار سیلاب با شدت {alert.trigger_data.get('rainfall_mm_hr', 0)}mm/hr. اقدامات فوری لازم است.",
            work_type="emergency_prevention",
            priority="urgent",
            structure_name="حوضه آبریز پایین‌دست",
            created_by="auto_ews",
            due_date=datetime.utcnow() + timedelta(hours=2),
            alert_id=alert.id,
            required_tools=["بیل", "کیسه شن", "پمپ آب", "بی‌سیم"],
            required_materials=["کیسه شن 500 عدد", "لوله PVC 10 متر"],
            estimated_duration_hours=4,
            estimated_cost=5000000  # 5 میلیون تومان
        )
        session.add(work_order)
        await session.flush()
        
        alert.auto_generated_work_orders = [work_order.id]
        logger.info(f"📝 Flood work order generated: {work_order.work_order_number}")
    
    async def _generate_inspection_work_order(self, session: AsyncSession, alert: EarlyWarningAlert):
        """تولید خودکار دستور کار بازرسی"""
        work_order = MaintenanceWorkOrder(
            work_order_number=f"WO-INSP-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            title="بازرسی فوری سازه",
            description=f"تغییر ناگهانی در دبی detected. بازرسی فوری برای بررسی علت لازم است.",
            work_type="inspection",
            priority="high",
            structure_name="سازه آبخیزداری",
            created_by="auto_ews",
            due_date=datetime.utcnow() + timedelta(hours=6),
            alert_id=alert.id,
            required_tools=["دوربین", "متر لیزری", "چراغ قوه", "دفترچه بازرسی"],
            estimated_duration_hours=2,
            estimated_cost=500000  # 500 هزار تومان
        )
        session.add(work_order)
        await session.flush()
        
        alert.auto_generated_work_orders = [work_order.id]
        logger.info(f"📝 Inspection work order generated: {work_order.work_order_number}")
    
    def stop(self):
        """توقف موتور"""
        self.running = False
        logger.info("🛑 Early Warning Engine stopped")


# Singleton instance
ews_engine = EarlyWarningEngine()
'''
    
    write_file(API_DIR / "services" / "early_warning_engine.py", content)


# ========== 3. بک‌اند: Router برای مدیریت نگهداشت ==========
def create_maintenance_router():
    print("\n🔧 ایجاد Router نگهداشت...")
    
    content = '''# api/modules/maintenance/router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

from api.core.database import get_db
from api.modules.maintenance.models import (
    EarlyWarningAlert, MaintenanceWorkOrder, ClimateRiskScenario
)

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


@router.post("/alerts/{alert_id}/acknowledge")
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


@router.put("/work-orders/{work_order_id}")
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


@router.get("/stats")
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
'''
    
    write_file(API_DIR / "modules" / "maintenance" / "router.py", content)


# ========== 4. بک‌اند: __init__.py ==========
def create_maintenance_init():
    print("\n📦 ایجاد maintenance/__init__.py...")
    
    content = '''# api/modules/maintenance/__init__.py
from . import models
from . import router
'''
    
    write_file(API_DIR / "modules" / "maintenance" / "__init__.py", content)


# ========== 5. به‌روزرسانی main.py ==========
def update_main():
    print("\n🔧 به‌روزرسانی main.py...")
    
    main_path = API_DIR / "main.py"
    if not main_path.exists():
        print("   ❌ main.py یافت نشد")
        return
    
    content = main_path.read_text(encoding="utf-8")
    
    # اضافه کردن import ها
    if "maintenance_router" not in content:
        content = content.replace(
            "from api.modules.iot.router import router as iot_router",
            "from api.modules.iot.router import router as iot_router\nfrom api.modules.maintenance.router import router as maintenance_router"
        )
        
        # اضافه کردن ثبت router
        content = content.replace(
            'app.include_router(iot_router, prefix="/api/v1")',
            'app.include_router(iot_router, prefix="/api/v1")\napp.include_router(maintenance_router, prefix="/api/v1")'
        )
        
        # اضافه کردن شروع EWS
        if "ews_engine" not in content:
            content = content.replace(
                "print(\"Ready on http://127.0.0.1:8000\")",
                "print(\"Ready on http://127.0.0.1:8000\")\n    \n    # شروع Early Warning Engine\n    try:\n        from api.services.early_warning_engine import ews_engine\n        import asyncio\n        asyncio.create_task(ews_engine.start())\n        print(\"✅ Early Warning Engine started\")\n    except Exception as e:\n        print(f\"⚠️ EWS skipped: {e}\")"
            )
        
        main_path.write_text(content, encoding="utf-8")
        print("   ✅ main.py به‌روز شد")
    else:
        print("   ℹ️  از قبل به‌روز شده")


# ========== 6. فرانت‌اند: داشبورد نگهداشت ==========
def create_maintenance_dashboard():
    print("\n📊 ایجاد داشبورد نگهداشت...")
    
    content = '''"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  ArrowRight, AlertTriangle, Wrench, Clock, CheckCircle, 
  TrendingUp, MapPin, Calendar, Users, RefreshCw
} from "lucide-react";

interface Alert {
  id: number;
  alert_type: string;
  severity: string;
  title: string;
  description: string;
  affected_area: string;
  confidence_level: number;
  detected_at: string;
  expected_impact_at: string;
  is_active: boolean;
  acknowledged: boolean;
  recommended_actions: string[];
}

interface WorkOrder {
  id: number;
  work_order_number: string;
  title: string;
  description: string;
  work_type: string;
  priority: string;
  status: string;
  structure_name: string;
  location_name: string;
  created_at: string;
  due_date: string;
  assigned_to: string;
  estimated_duration_hours: number;
  estimated_cost: number;
}

interface Stats {
  active_alerts: number;
  pending_work_orders: number;
  in_progress_work_orders: number;
  completed_work_orders: number;
  overdue_work_orders: number;
}

const SEVERITY_COLORS = {
  info: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  warning: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  critical: "bg-red-500/20 text-red-400 border-red-500/30",
  emergency: "bg-red-700/20 text-red-600 border-red-700/30"
};

const PRIORITY_COLORS = {
  low: "bg-slate-500/20 text-slate-400",
  medium: "bg-blue-500/20 text-blue-400",
  high: "bg-amber-500/20 text-amber-400",
  urgent: "bg-red-500/20 text-red-400"
};

const STATUS_COLORS = {
  pending: "bg-slate-500/20 text-slate-400",
  assigned: "bg-blue-500/20 text-blue-400",
  in_progress: "bg-amber-500/20 text-amber-400",
  completed: "bg-emerald-500/20 text-emerald-400",
  cancelled: "bg-red-500/20 text-red-400"
};

export default function MaintenanceDashboardPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"alerts" | "work-orders">("alerts");

  const fetchData = async () => {
    try {
      const [alertsRes, woRes, statsRes] = await Promise.all([
        fetch("http://localhost:8000/api/v1/maintenance/alerts"),
        fetch("http://localhost:8000/api/v1/maintenance/work-orders"),
        fetch("http://localhost:8000/api/v1/maintenance/stats")
      ]);
      
      if (alertsRes.ok) setAlerts(await alertsRes.json());
      if (woRes.ok) setWorkOrders(await woRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const acknowledgeAlert = async (alertId: number) => {
    try {
      await fetch(`http://localhost:8000/api/v1/maintenance/alerts/${alertId}/acknowledge`, {
        method: "POST"
      });
      fetchData();
    } catch (error) {
      console.error("Failed to acknowledge alert:", error);
    }
  };

  const updateWorkOrderStatus = async (woId: number, status: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/maintenance/work-orders/${woId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status })
      });
      fetchData();
    } catch (error) {
      console.error("Failed to update work order:", error);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500 to-red-600 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-16">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-6 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-6">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-orange-500 to-red-600 shadow-2xl">
                <Wrench className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-orange-400 text-sm font-medium mb-2">Adaptive Maintenance</p>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">داشبورد نگهداشت</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  مدیریت هوشمند هشدارها و دستور کارهای نگهداری با سیستم خودکار تولید و اولویت‌بندی
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-4 text-sm text-slate-400">
              <span className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                Live Monitoring
              </span>
              <button 
                onClick={fetchData}
                className="flex items-center gap-2 px-3 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                بروزرسانی
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { label: "هشدارهای فعال", value: stats?.active_alerts || 0, icon: AlertTriangle, color: "#ef4444" },
            { label: "دستور کار در انتظار", value: stats?.pending_work_orders || 0, icon: Clock, color: "#f59e0b" },
            { label: "در حال انجام", value: stats?.in_progress_work_orders || 0, icon: Wrench, color: "#3b82f6" },
            { label: "تکمیل شده", value: stats?.completed_work_orders || 0, icon: CheckCircle, color: "#10b981" },
            { label: "عقب‌افتاده", value: stats?.overdue_work_orders || 0, icon: AlertTriangle, color: "#dc2626" },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6"
            >
              <stat.icon className="h-8 w-8 mb-3" style={{ color: stat.color }} />
              <p className="text-3xl font-black text-white mb-1">{stat.value}</p>
              <p className="text-sm text-slate-400">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Tabs */}
      <section className="container mx-auto px-6 py-8">
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab("alerts")}
            className={`px-6 py-3 rounded-xl font-bold transition-all ${
              activeTab === "alerts"
                ? "bg-orange-600 text-white"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            <AlertTriangle className="h-5 w-5 inline mr-2" />
            هشدارها ({alerts.length})
          </button>
          <button
            onClick={() => setActiveTab("work-orders")}
            className={`px-6 py-3 rounded-xl font-bold transition-all ${
              activeTab === "work-orders"
                ? "bg-orange-600 text-white"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            <Wrench className="h-5 w-5 inline mr-2" />
            دستور کارها ({workOrders.length})
          </button>
        </div>

        {/* Alerts Tab */}
        {activeTab === "alerts" && (
          <div className="space-y-4">
            {alerts.length === 0 ? (
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-12 text-center">
                <CheckCircle className="h-16 w-16 text-emerald-400 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-white mb-2">همه چیز تحت کنترل است</h3>
                <p className="text-slate-400">هیچ هشدار فعالی وجود ندارد</p>
              </div>
            ) : (
              alerts.map((alert, i) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className={`bg-slate-900/50 backdrop-blur-xl border-2 rounded-2xl p-6 ${
                    alert.severity === "critical" || alert.severity === "emergency"
                      ? "border-red-500/50"
                      : "border-slate-800"
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div className={`p-3 rounded-xl ${SEVERITY_COLORS[alert.severity as keyof typeof SEVERITY_COLORS]}`}>
                      <AlertTriangle className="h-6 w-6" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="text-xl font-bold text-white mb-1">{alert.title}</h3>
                          <div className="flex items-center gap-3 text-sm text-slate-400">
                            <span className={`px-2 py-1 rounded-full ${SEVERITY_COLORS[alert.severity as keyof typeof SEVERITY_COLORS]}`}>
                              {alert.severity}
                            </span>
                            <span>{new Date(alert.detected_at).toLocaleString("fa-IR")}</span>
                          </div>
                        </div>
                        {!alert.acknowledged && (
                          <button
                            onClick={() => acknowledgeAlert(alert.id)}
                            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-bold transition-colors"
                          >
                            تأیید
                          </button>
                        )}
                      </div>
                      <p className="text-slate-300 mb-4">{alert.description}</p>
                      
                      {alert.recommended_actions && alert.recommended_actions.length > 0 && (
                        <div className="bg-slate-800/50 rounded-xl p-4">
                          <h4 className="font-bold text-white mb-2">اقدامات پیشنهادی:</h4>
                          <ul className="space-y-1">
                            {alert.recommended_actions.map((action, idx) => (
                              <li key={idx} className="text-sm text-slate-300 flex items-start gap-2">
                                <span className="text-emerald-400 mt-0.5">▸</span>
                                <span>{action}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        )}

        {/* Work Orders Tab */}
        {activeTab === "work-orders" && (
          <div className="space-y-4">
            {workOrders.length === 0 ? (
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-12 text-center">
                <Wrench className="h-16 w-16 text-slate-600 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-white mb-2">دستور کاری وجود ندارد</h3>
                <p className="text-slate-400">هیچ دستور کار فعالی ثبت نشده است</p>
              </div>
            ) : (
              workOrders.map((wo, i) => (
                <motion.div
                  key={wo.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-xs text-slate-500 font-mono">{wo.work_order_number}</span>
                        <span className={`px-2 py-1 rounded-full text-xs ${PRIORITY_COLORS[wo.priority as keyof typeof PRIORITY_COLORS]}`}>
                          {wo.priority}
                        </span>
                        <span className={`px-2 py-1 rounded-full text-xs ${STATUS_COLORS[wo.status as keyof typeof STATUS_COLORS]}`}>
                          {wo.status}
                        </span>
                      </div>
                      <h3 className="text-xl font-bold text-white mb-1">{wo.title}</h3>
                      <p className="text-sm text-slate-400">{wo.description}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
                    <div>
                      <p className="text-slate-500 mb-1">محل</p>
                      <p className="text-white flex items-center gap-1">
                        <MapPin className="h-3 w-3" /> {wo.location_name || wo.structure_name}
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-500 mb-1">مهلت</p>
                      <p className="text-white flex items-center gap-1">
                        <Calendar className="h-3 w-3" /> {wo.due_date ? new Date(wo.due_date).toLocaleDateString("fa-IR") : "نامشخص"}
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-500 mb-1">مدت تخمینی</p>
                      <p className="text-white flex items-center gap-1">
                        <Clock className="h-3 w-3" /> {wo.estimated_duration_hours || 0} ساعت
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-500 mb-1">هزینه تخمینی</p>
                      <p className="text-white">{wo.estimated_cost?.toLocaleString() || 0} تومان</p>
                    </div>
                  </div>
                  
                  {wo.status !== "completed" && (
                    <div className="flex gap-2">
                      {wo.status === "pending" && (
                        <button
                          onClick={() => updateWorkOrderStatus(wo.id, "assigned")}
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-bold transition-colors"
                        >
                          واگذاری
                        </button>
                      )}
                      {wo.status === "assigned" && (
                        <button
                          onClick={() => updateWorkOrderStatus(wo.id, "in_progress")}
                          className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-sm font-bold transition-colors"
                        >
                          شروع کار
                        </button>
                      )}
                      {wo.status === "in_progress" && (
                        <button
                          onClick={() => updateWorkOrderStatus(wo.id, "completed")}
                          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-bold transition-colors"
                        >
                          تکمیل
                        </button>
                      )}
                    </div>
                  )}
                </motion.div>
              ))
            )}
          </div>
        )}
      </section>
    </div>
  );
}
'''
    
    write_file(WEB / "app" / "maintenance" / "page.tsx", content)


# ========== Main ==========
def main():
    print("🛡️ لایه 3: نگهداشت تطبیقی و مدیریت ریسک")
    print("=" * 70)
    
    if not API_DIR.exists() or not WEB.exists():
        print("❌ دایرکتوری‌های مورد نیاز یافت نشد!")
        return 1
    
    create_maintenance_models()
    create_maintenance_init()
    create_ews_engine()
    create_maintenance_router()
    update_main()
    create_maintenance_dashboard()
    
    print("\n" + "=" * 70)
    print("✅ لایه 3 تکمیل شد!")
    print("\n🎯 ویژگی‌های ایجاد شده:")
    print("   1. ✅ سیستم هشدار زودهنگام هیبریدی")
    print("      • تشخیص سیلاب (بارش > 50mm/hr)")
    print("      • تشخیص خشکسالی (رطوبت < 15%)")
    print("      • تشخیص خرابی سازه (تغییر > 50%)")
    print("      • تشخیص تنش آبی (تلفات > 30%)")
    print("")
    print("   2. ✅ موتور تولید خودکار دستور کار")
    print("      • تولید دستور کار فوری برای سیلاب")
    print("      • تولید دستور کار بازرسی برای خرابی")
    print("      • اولویت‌بندی خودکار")
    print("")
    print("   3. ✅ داشبورد مدیریت نگهداشت")
    print("      • نمایش هشدارهای فعال")
    print("      • مدیریت دستور کارها")
    print("      • آمار لحظه‌ای")
    print("      • تأیید و به‌روزرسانی وضعیت")
    
    print("\n🚀 گام بعدی:")
    print("   1. پاک‌سازی کش:")
    print("      cd apps\\web")
    print("      Remove-Item .next -Recurse -Force")
    print("")
    print("   2. اجرای سرور بک‌اند:")
    print("      uvicorn api.main:app --reload --port 8000")
    print("")
    print("   3. اجرای سرور فرانت‌اند:")
    print("      cd apps\\web")
    print("      pnpm run dev -- -p 3001")
    print("")
    print("   4. مشاهده:")
    print("      • داشبورد نگهداشت: http://localhost:3001/maintenance")
    print("      • API Docs: http://localhost:8000/docs")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())