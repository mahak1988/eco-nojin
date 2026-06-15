"""Dashboard Service - Management Dashboards for Stakeholders

این سرویس داشبوردهای تخصصی برای چهار گروه ذی‌نفع را ایجاد می‌کند:
۱. مدیران حوضه آبخیز
۲. کشاورزان
۳. سرمایه‌گذاران
۴. سیاست‌گذاران
"""
from typing import Dict, List
from datetime import datetime
from .models.dashboard_models import (
    DashboardType,
    DashboardWidget,
    KPI,
    KPI_Category,
    AlertNotification
)
from .services.dss_service import DSSService
import uuid


class DashboardService:
    """سرویس مدیریت داشبوردها"""
    
    def __init__(self):
        self.dss = DSSService()
    
    def get_watershed_manager_dashboard(self, watershed_id: str) -> Dict:
        """داشبورد مدیر حوضه آبخیز"""
        widgets = []
        
        # ویجت 1: شاخص‌های آب
        water_kpis = [
            KPI("wue", "بهره‌وری آب", KPI_Category.WATER, 1.2, "kg/m3", 1.5, 0.8, "improving"),
            KPI("groundwater_level", "سطح آب زیرزمینی", KPI_Category.WATER, 12.5, "m", 10.0, 15.0, "stable"),
            KPI("water_stress", "شاخص تنش آبی", KPI_Category.WATER, 0.65, "ratio", 0.5, 0.8, "improving")
        ]
        
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.WATERSHED_MANAGER,
            "title": "شاخص‌های منابع آب",
            "widget_type": "metric",
            "kpis": water_kpis,
            "configuration": {"layout": "grid"}
        })
        
        # ویجت 2: شاخص‌های خاک
        soil_kpis = [
            KPI("soc", "کربن آلی خاک", KPI_Category.SOIL, 2.3, "%", 3.0, 1.5, "improving"),
            KPI("erosion_rate", "نرخ فرسایش", KPI_Category.SOIL, 8.5, "t/ha/year", 5.0, 15.0, "improving"),
            KPI("ldn_progress", "پیشرفت به سمت LDN", KPI_Category.SOIL, 0.72, "ratio", 1.0, 0.5, "improving")
        ]
        
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.WATERSHED_MANAGER,
            "title": "شاخص‌های خاک و سرزمین",
            "widget_type": "metric",
            "kpis": soil_kpis,
            "configuration": {"layout": "grid"}
        })
        
        # ویجت 3: نقشه پوشش گیاهی
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.WATERSHED_MANAGER,
            "title": "نقشه NDVI و پوشش گیاهی",
            "widget_type": "map",
            "kpis": [],
            "configuration": {"layer": "ndvi", "watershed_id": watershed_id}
        })
        
        # ویجت 4: نمودار روند
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.WATERSHED_MANAGER,
            "title": "روند تغییرات شاخص‌ها",
            "widget_type": "chart",
            "kpis": [],
            "configuration": {"chart_type": "line", "metrics": ["ndvi", "soc", "wue"]}
        })
        
        # تولید توصیه‌های DSS
        water_assessment = self.dss.evaluate_water_stress(1.2, 12.5, -10)
        soil_assessment = self.dss.evaluate_soil_health(2.3, 8.5, 2.5)
        
        recommendations = {
            "water": water_assessment,
            "soil": soil_assessment
        }
        
        return {
            "dashboard_type": DashboardType.WATERSHED_MANAGER,
            "title": "داشبورد مدیر حوضه آبخیز",
            "watershed_id": watershed_id,
            "widgets": widgets,
            "recommendations": recommendations,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_farmer_dashboard(self, farmer_id: str, farm_id: str) -> Dict:
        """داشبورد کشاورز"""
        widgets = []
        
        # ویجت 1: وضعیت مزرعه
        farm_kpis = [
            KPI("soil_moisture", "رطوبت خاک", KPI_Category.SOIL, 28.5, "%", 30.0, 20.0, "stable"),
            KPI("crop_health", "سلامت محصول", KPI_Category.ECOSYSTEM, 0.78, "NDVI", 0.8, 0.6, "improving"),
            KPI("water_need", "نیاز آبی", KPI_Category.WATER, 45.0, "mm/day", 40.0, 50.0, "stable")
        ]
        
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.FARMER,
            "title": "وضعیت مزرعه من",
            "widget_type": "metric",
            "kpis": farm_kpis,
            "configuration": {"layout": "list"}
        })
        
        # ویجت 2: توصیه آبیاری
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.FARMER,
            "title": "توصیه آبیاری امروز",
            "widget_type": "alert",
            "kpis": [],
            "configuration": {
                "message": "آبیاری فردا صبح زود - ۳۰ میلی‌متر",
                "priority": "medium"
            }
        })
        
        # ویجت 3: پیش‌بینی هوا
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.FARMER,
            "title": "پیش‌بینی هوا ۷ روز",
            "widget_type": "chart",
            "kpis": [],
            "configuration": {"chart_type": "weather", "days": 7}
        })
        
        # ویجت 4: درآمد
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.FARMER,
            "title": "درآمد این فصل",
            "widget_type": "metric",
            "kpis": [
                KPI("income", "درآمد", KPI_Category.LIVELIHOOD, 15000000, "IRR", 20000000, 10000000, "improving")
            ],
            "configuration": {"layout": "single"}
        })
        
        return {
            "dashboard_type": DashboardType.FARMER,
            "title": "داشبورد کشاورز",
            "farmer_id": farmer_id,
            "farm_id": farm_id,
            "widgets": widgets,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_investor_dashboard(self, project_id: str) -> Dict:
        """داشبورد سرمایه‌گذار"""
        widgets = []
        
        # ویجت 1: شاخص‌های مالی
        financial_kpis = [
            KPI("npv", "ارزش فعلی خالص", KPI_Category.LIVELIHOOD, 250000, "USD", 300000, 200000, "improving"),
            KPI("irr", "نرخ بازده داخلی", KPI_Category.LIVELIHOOD, 0.18, "ratio", 0.20, 0.12, "improving"),
            KPI("payback_period", "دوره بازگشت", KPI_Category.LIVELIHOOD, 5.2, "years", 5.0, 7.0, "improving")
        ]
        
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.INVESTOR,
            "title": "شاخص‌های مالی پروژه",
            "widget_type": "metric",
            "kpis": financial_kpis,
            "configuration": {"layout": "grid"}
        })
        
        # ویجت 2: اعتبارات کربن
        carbon_kpis = [
            KPI("carbon_credits", "اعتبارات کربن صادرشده", KPI_Category.CARBON, 1500, "tCO2e", 2000, 1000, "improving"),
            KPI("carbon_revenue", "درآمد کربن", KPI_Category.CARBON, 37500, "USD", 50000, 25000, "improving")
        ]
        
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.INVESTOR,
            "title": "اعتبارات کربن",
            "widget_type": "metric",
            "kpis": carbon_kpis,
            "configuration": {"layout": "grid"}
        })
        
        # ویجت 3: تأثیر اجتماعی
        social_kpis = [
            KPI("beneficiaries", "خانوار بهره‌مند", KPI_Category.LIVELIHOOD, 450, "households", 500, 300, "improving"),
            KPI("jobs_created", "اشتغال ایجادشده", KPI_Category.LIVELIHOOD, 120, "jobs", 150, 80, "improving")
        ]
        
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.INVESTOR,
            "title": "تأثیر اجتماعی",
            "widget_type": "metric",
            "kpis": social_kpis,
            "configuration": {"layout": "grid"}
        })
        
        # ویجت 4: نمودار جریان نقدی
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.INVESTOR,
            "title": "جریان نقدی پیش‌بینی‌شده",
            "widget_type": "chart",
            "kpis": [],
            "configuration": {"chart_type": "cashflow", "years": 10}
        })
        
        return {
            "dashboard_type": DashboardType.INVESTOR,
            "title": "داشبورد سرمایه‌گذار",
            "project_id": project_id,
            "widgets": widgets,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_policy_maker_dashboard(self, region_id: str) -> Dict:
        """داشبورد سیاست‌گذار"""
        widgets = []
        
        # ویجت 1: پیشرفت SDGs
        sdg_kpis = [
            KPI("sdg2_progress", "پیشرفت SDG 2 (غذا)", KPI_Category.LIVELIHOOD, 0.68, "ratio", 1.0, 0.5, "improving"),
            KPI("sdg6_progress", "پیشرفت SDG 6 (آب)", KPI_Category.WATER, 0.62, "ratio", 1.0, 0.4, "improving"),
            KPI("sdg13_progress", "پیشرفت SDG 13 (اقلیم)", KPI_Category.CARBON, 0.55, "ratio", 1.0, 0.3, "improving"),
            KPI("sdg15_progress", "پیشرفت SDG 15 (زمین)", KPI_Category.SOIL, 0.71, "ratio", 1.0, 0.5, "improving")
        ]
        
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.POLICY_MAKER,
            "title": "پیشرفت اهداف توسعه پایدار",
            "widget_type": "metric",
            "kpis": sdg_kpis,
            "configuration": {"layout": "grid"}
        })
        
        # ویجت 2: نقشه منطقه‌ای
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.POLICY_MAKER,
            "title": "نقشه وضعیت منطقه",
            "widget_type": "map",
            "kpis": [],
            "configuration": {"layer": "composite", "region_id": region_id}
        })
        
        # ویجت 3: مقایسه پایلوت‌ها
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.POLICY_MAKER,
            "title": "مقایسه عملکرد پایلوت‌ها",
            "widget_type": "chart",
            "kpis": [],
            "configuration": {"chart_type": "bar", "pilots": ["dishmok", "behbahan", "rodbar", "yasouj"]}
        })
        
        # ویجت 4: گزارش NDC
        ndc_kpis = [
            KPI("ndc_contribution", "سهم در NDC", KPI_Category.CARBON, 12.5, "percent", 15.0, 8.0, "improving"),
            KPI("ldn_target", "پیشرفت به سمت LDN", KPI_Category.SOIL, 0.72, "ratio", 1.0, 0.5, "improving")
        ]
        
        widgets.append({
            "widget_id": str(uuid.uuid4()),
            "dashboard_type": DashboardType.POLICY_MAKER,
            "title": "تعهدات ملی و بین‌المللی",
            "widget_type": "metric",
            "kpis": ndc_kpis,
            "configuration": {"layout": "grid"}
        })
        
        return {
            "dashboard_type": DashboardType.POLICY_MAKER,
            "title": "داشبورد سیاست‌گذار",
            "region_id": region_id,
            "widgets": widgets,
            "last_updated": datetime.utcnow().isoformat()
        }
