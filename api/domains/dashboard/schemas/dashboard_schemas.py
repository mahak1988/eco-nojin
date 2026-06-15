"""Dashboard Domain Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from .models.dashboard_models import DashboardType, KPI_Category


class KPIResponse(BaseModel):
    """اسکیما پاسخ شاخص"""
    kpi_id: str
    name: str
    category: KPI_Category
    value: float
    unit: str
    target_value: Optional[float]
    baseline_value: Optional[float]
    trend: str
    last_updated: datetime
    
    class Config:
        from_attributes = True


class DashboardWidgetResponse(BaseModel):
    """اسکیما پاسخ ویجت"""
    widget_id: str
    dashboard_type: DashboardType
    title: str
    widget_type: str
    kpis: List[KPIResponse]
    configuration: Dict
    
    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    """اسکیما پاسخ داشبورد کامل"""
    dashboard_type: DashboardType
    title: str
    widgets: List[DashboardWidgetResponse]
    alerts: List[Dict]
    last_updated: datetime


class AlertNotificationResponse(BaseModel):
    """اسکیما پاسخ هشدار"""
    alert_id: str
    dashboard_type: DashboardType
    severity: str
    title: str
    message: str
    timestamp: datetime
    acknowledged: bool
    
    class Config:
        from_attributes = True


class UserPreferenceRequest(BaseModel):
    """درخواست تنظیمات کاربر"""
    preferred_kpis: List[str] = []
    alert_thresholds: Dict = {}
    language: str = "fa"
    theme: str = "light"
