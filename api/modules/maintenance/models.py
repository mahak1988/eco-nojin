# api/modules/maintenance/models.py
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
