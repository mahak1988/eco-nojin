"""Coupling Engine - Central Integration Hub

این ماژول تمام سرویس‌های DDD را به هم متصل می‌کند و گردش کارهای پیچیده
را بین دامنه‌های مختلف مدیریت می‌نماید.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import json


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowStep:
    step_id: str
    domain: str
    service: str
    method: str
    parameters: Dict = field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None


@dataclass
class CoupledWorkflow:
    workflow_id: str
    name: str
    pilot_site: str
    steps: List[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class CouplingEngine:
    """موتور اتصال مرکزی برای یکپارچه‌سازی تمام سرویس‌ها"""
    
    def __init__(self):
        self.workflows: Dict[str, CoupledWorkflow] = {}
        self.domain_services = {}
        self._register_domain_services()
    
    def _register_domain_services(self):
        """ثبت تمام سرویس‌های دامنه‌ها"""
        self.domain_services = {
            'drought': {
                'service': 'DroughtService',
                'methods': ['calculate_spei', 'classify_drought_severity', 'get_early_warning']
            },
            'soil_water': {
                'service': 'SoilWaterService',
                'methods': ['calculate_rusle', 'analyze_soil_health', 'get_erosion_assessment']
            },
            'financial': {
                'service': 'FinancialService',
                'methods': ['calculate_npv', 'calculate_irr', 'evaluate_project', 'issue_carbon_credit']
            },
            'iot': {
                'service': 'IoTService',
                'methods': ['get_device_readings', 'check_drought_conditions', 'check_flood_risk']
            },
            'hydrology': {
                'service': 'HydrologyService',
                'methods': ['run_swat_simulation', 'run_weap_allocation', 'analyze_climate_scenario']
            },
            'remote_sensing': {
                'service': 'RemoteSensingService',
                'methods': ['calculate_ndvi', 'calculate_ndwi', 'analyze_vegetation_health']
            },
            'mrv': {
                'service': 'MRVService',
                'methods': ['calculate_soc_change', 'calculate_n2o_emissions', 'generate_mrv_report']
            },
            'dashboard': {
                'service': 'DashboardService',
                'methods': ['get_watershed_manager_dashboard', 'get_farmer_dashboard', 'get_investor_dashboard']
            },
            'training': {
                'service': 'TrainingService',
                'methods': ['get_modules_by_pilot', 'schedule_session', 'issue_certificate']
            },
            'psychology': {
                'service': 'PsychologyService',
                'methods': ['submit_test', 'interpret_result']
            }
        }
    
    def create_workflow(self, name: str, pilot_site: str) -> CoupledWorkflow:
        """ایجاد یک گردش کار جدید"""
        import uuid
        workflow_id = str(uuid.uuid4())
        workflow = CoupledWorkflow(
            workflow_id=workflow_id,
            name=name,
            pilot_site=pilot_site
        )
        self.workflows[workflow_id] = workflow
        return workflow
    
    def add_step(
        self,
        workflow_id: str,
        domain: str,
        service: str,
        method: str,
        parameters: Dict = None
    ) -> Optional[WorkflowStep]:
        """افزودن یک گام به گردش کار"""
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        step = WorkflowStep(
            step_id=f"step_{len(workflow.steps) + 1}",
            domain=domain,
            service=service,
            method=method,
            parameters=parameters or {}
        )
        workflow.steps.append(step)
        return step
    
    def execute_workflow(self, workflow_id: str) -> Dict:
        """اجرای گردش کار"""
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}
        
        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.RUNNING
        
        results = []
        for step in workflow.steps:
            step.status = WorkflowStatus.RUNNING
            
            # شبیه‌سازی اجرا (در واقعیت باید سرویس واقعی فراخوانی شود)
            try:
                result = self._execute_step(step)
                step.result = result
                step.status = WorkflowStatus.COMPLETED
                results.append(result)
            except Exception as e:
                step.error = str(e)
                step.status = WorkflowStatus.FAILED
                workflow.status = WorkflowStatus.FAILED
                break
        
        if workflow.status == WorkflowStatus.RUNNING:
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now(timezone.utc)
        
        return {
            "workflow_id": workflow_id,
            "status": workflow.status.value,
            "steps_completed": sum(1 for s in workflow.steps if s.status == WorkflowStatus.COMPLETED),
            "total_steps": len(workflow.steps),
            "results": results
        }
    
    def _execute_step(self, step: WorkflowStep) -> Dict:
        """اجرای یک گام (شبیه‌سازی)"""
        # در واقعیت باید سرویس واقعی فراخوانی شود
        return {
            "step_id": step.step_id,
            "domain": step.domain,
            "method": step.method,
            "status": "success",
            "data": {"message": f"Executed {step.method} on {step.domain}"}
        }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict]:
        """دریافت وضعیت گردش کار"""
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "pilot_site": workflow.pilot_site,
            "status": workflow.status.value,
            "steps": [
                {
                    "step_id": s.step_id,
                    "domain": s.domain,
                    "method": s.method,
                    "status": s.status.value
                }
                for s in workflow.steps
            ]
        }
    
    def get_all_workflows(self) -> List[Dict]:
        """دریافت تمام گردش کارها"""
        return [
            {
                "workflow_id": wf.workflow_id,
                "name": wf.name,
                "pilot_site": wf.pilot_site,
                "status": wf.status.value,
                "steps_count": len(wf.steps)
            }
            for wf in self.workflows.values()
        ]
