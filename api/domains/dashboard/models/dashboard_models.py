"""Dashboard Domain Models"""
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class DashboardType(str, Enum):
    """انواع داشبورد"""
    WATERSHED_MANAGER = "watershed_manager"
    FARMER = "farmer"
    INVESTOR = "investor"
    POLICY_MAKER = "policy_maker"


class KPI_Category(str, Enum):
    """دسته‌بندی شاخص‌های کلیدی عملکرد"""
    WATER = "water"
    SOIL = "soil"
    ECOSYSTEM = "ecosystem"
    LIVELIHOOD = "livelihood"
    CARBON = "carbon"
    GOVERNANCE = "governance"


@dataclass
class KPI:
    """نماینده یک شاخص کلیدی عملکرد"""
    kpi_id: str
    name: str
    category: KPI_Category
    value: float
    unit: str
    target_value: Optional[float] = None
    baseline_value: Optional[float] = None
    trend: str = "stable"  # improving, degrading, stable
    last_updated: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)


@dataclass
class DashboardWidget:
    """نماینده یک ویجت داشبورد"""
    widget_id: str
    dashboard_type: DashboardType
    title: str
    widget_type: str  # chart, map, table, metric
    data_source: str
    kpis: List[KPI] = field(default_factory=list)
    configuration: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AlertNotification:
    """نماینده یک هشدار در داشبورد"""
    alert_id: str
    dashboard_type: DashboardType
    severity: str  # info, warning, critical
    title: str
    message: str
    kpi_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False


@dataclass
class UserPreference:
    """تنظیمات کاربر برای داشبورد"""
    user_id: str
    dashboard_type: DashboardType
    preferred_kpis: List[str] = field(default_factory=list)
    alert_thresholds: Dict = field(default_factory=dict)
    language: str = "fa"
    theme: str = "light"
