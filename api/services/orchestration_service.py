"""Orchestration Service - Complex Workflow Management

این سرویس گردش کارهای پیچیده بین دامنه‌های مختلف را مدیریت می‌کند.
"""
from typing import Dict, List
from datetime import datetime, timezone
from api.core.coupling_engine import CouplingEngine


class OrchestrationService:
    """سرویس orchestration برای گردش کارهای پیچیده"""
    
    def __init__(self):
        self.engine = CouplingEngine()
    
    def create_comprehensive_assessment_workflow(
        self,
        pilot_site: str,
        lat: float,
        lon: float
    ) -> Dict:
        """ایجاد گردش کار ارزیابی جامع"""
        workflow = self.engine.create_workflow(
            name="Comprehensive Landscape Assessment",
            pilot_site=pilot_site
        )
        
        # گام 1: دریافت داده‌های IoT
        self.engine.add_step(
            workflow.workflow_id,
            domain="iot",
            service="IoTService",
            method="get_device_readings",
            parameters={"lat": lat, "lon": lon}
        )
        
        # گام 2: تحلیل سنجش‌ازدور
        self.engine.add_step(
            workflow.workflow_id,
            domain="remote_sensing",
            service="RemoteSensingService",
            method="calculate_ndvi",
            parameters={"lat": lat, "lon": lon}
        )
        
        # گام 3: ارزیابی خشکسالی
        self.engine.add_step(
            workflow.workflow_id,
            domain="drought",
            service="DroughtService",
            method="get_early_warning",
            parameters={"lat": lat, "lon": lon}
        )
        
        # گام 4: تحلیل خاک
        self.engine.add_step(
            workflow.workflow_id,
            domain="soil_water",
            service="SoilWaterService",
            method="analyze_soil_health",
            parameters={"lat": lat, "lon": lon}
        )
        
        # گام 5: محاسبه MRV
        self.engine.add_step(
            workflow.workflow_id,
            domain="mrv",
            service="MRVService",
            method="generate_mrv_report",
            parameters={"pilot_site": pilot_site}
        )
        
        # گام 6: تولید داشبورد
        self.engine.add_step(
            workflow.workflow_id,
            domain="dashboard",
            service="DashboardService",
            method="get_watershed_manager_dashboard",
            parameters={"watershed_id": pilot_site}
        )
        
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "steps_count": len(workflow.steps)
        }
    
    def create_investment_evaluation_workflow(
        self,
        project_id: str,
        pilot_site: str
    ) -> Dict:
        """ایجاد گردش کار ارزیابی سرمایه‌گذاری"""
        workflow = self.engine.create_workflow(
            name="Investment Evaluation",
            pilot_site=pilot_site
        )
        
        # گام 1: محاسبه NPV
        self.engine.add_step(
            workflow.workflow_id,
            domain="financial",
            service="FinancialService",
            method="calculate_npv",
            parameters={"project_id": project_id}
        )
        
        # گام 2: محاسبه IRR
        self.engine.add_step(
            workflow.workflow_id,
            domain="financial",
            service="FinancialService",
            method="calculate_irr",
            parameters={"project_id": project_id}
        )
        
        # گام 3: ارزیابی پروژه
        self.engine.add_step(
            workflow.workflow_id,
            domain="financial",
            service="FinancialService",
            method="evaluate_project",
            parameters={"project_id": project_id}
        )
        
        # گام 4: صدور اعتبار کربن
        self.engine.add_step(
            workflow.workflow_id,
            domain="financial",
            service="FinancialService",
            method="issue_carbon_credit",
            parameters={"project_id": project_id}
        )
        
        # گام 5: تولید داشبورد سرمایه‌گذار
        self.engine.add_step(
            workflow.workflow_id,
            domain="dashboard",
            service="DashboardService",
            method="get_investor_dashboard",
            parameters={"project_id": project_id}
        )
        
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "steps_count": len(workflow.steps)
        }
    
    def execute_workflow(self, workflow_id: str) -> Dict:
        """اجرای گردش کار"""
        return self.engine.execute_workflow(workflow_id)
    
    def get_workflow_status(self, workflow_id: str) -> Dict:
        """دریافت وضعیت گردش کار"""
        return self.engine.get_workflow_status(workflow_id)
