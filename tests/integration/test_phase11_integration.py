"""تست‌های یکپارچگی سراسری - فاز ۱۱"""
import pytest
from datetime import datetime, timezone
from api.core.coupling_engine import CouplingEngine, WorkflowStatus
from api.services.orchestration_service import OrchestrationService


class TestCouplingEngine:
    """تست‌های Coupling Engine"""
    
    def test_create_workflow(self):
        """تست ایجاد گردش کار"""
        engine = CouplingEngine()
        workflow = engine.create_workflow(
            name="Test Workflow",
            pilot_site="dishmok"
        )
        
        assert workflow.workflow_id is not None
        assert workflow.name == "Test Workflow"
        assert workflow.pilot_site == "dishmok"
        assert workflow.status == WorkflowStatus.PENDING
    
    def test_add_step(self):
        """تست افزودن گام"""
        engine = CouplingEngine()
        workflow = engine.create_workflow("Test", "dishmok")
        
        step = engine.add_step(
            workflow.workflow_id,
            domain="drought",
            service="DroughtService",
            method="calculate_spei",
            parameters={"precipitation": [100, 80, 60]}
        )
        
        assert step is not None
        assert step.domain == "drought"
        assert step.method == "calculate_spei"
        assert len(workflow.steps) == 1
    
    def test_execute_workflow(self):
        """تست اجرای گردش کار"""
        engine = CouplingEngine()
        workflow = engine.create_workflow("Test", "dishmok")
        
        engine.add_step(
            workflow.workflow_id,
            domain="drought",
            service="DroughtService",
            method="calculate_spei"
        )
        
        engine.add_step(
            workflow.workflow_id,
            domain="soil_water",
            service="SoilWaterService",
            method="analyze_soil_health"
        )
        
        result = engine.execute_workflow(workflow.workflow_id)
        
        assert result["status"] == "completed"
        assert result["steps_completed"] == 2
        assert result["total_steps"] == 2
    
    def test_get_workflow_status(self):
        """تست دریافت وضعیت گردش کار"""
        engine = CouplingEngine()
        workflow = engine.create_workflow("Test", "dishmok")
        
        engine.add_step(
            workflow.workflow_id,
            domain="drought",
            service="DroughtService",
            method="calculate_spei"
        )
        
        status = engine.get_workflow_status(workflow.workflow_id)
        
        assert status is not None
        assert status["workflow_id"] == workflow.workflow_id
        assert len(status["steps"]) == 1


class TestOrchestrationService:
    """تست‌های Orchestration Service"""
    
    def test_create_comprehensive_assessment(self):
        """تست ایجاد ارزیابی جامع"""
        service = OrchestrationService()
        
        result = service.create_comprehensive_assessment_workflow(
            pilot_site="dishmok",
            lat=30.9,
            lon=51.4
        )
        
        assert "workflow_id" in result
        assert result["steps_count"] == 6
    
    def test_create_investment_evaluation(self):
        """تست ایجاد ارزیابی سرمایه‌گذاری"""
        service = OrchestrationService()
        
        result = service.create_investment_evaluation_workflow(
            project_id="project_001",
            pilot_site="dishmok"
        )
        
        assert "workflow_id" in result
        assert result["steps_count"] == 5
    
    def test_execute_workflow(self):
        """تست اجرای گردش کار"""
        service = OrchestrationService()
        
        workflow_result = service.create_comprehensive_assessment_workflow(
            pilot_site="dishmok",
            lat=30.9,
            lon=51.4
        )
        
        execution_result = service.execute_workflow(workflow_result["workflow_id"])
        
        assert execution_result["status"] == "completed"
        assert execution_result["steps_completed"] == 6


class TestGlobalIntegration:
    """تست‌های یکپارچگی جهانی"""
    
    def test_all_pilots_accessible(self):
        """تست دسترسی به تمام پایلوت‌ها"""
        pilots = [
            "dishmok", "behbahan", "rodbar_talesh", "snow_mountain",
            "ouarzazate", "wadi_rum", "sahel_senegal", "ethiopian_highlands",
            "rajasthan", "outback_australia", "atacama_chile", "mongolian_steppe"
        ]
        
        service = OrchestrationService()
        
        for pilot in pilots:
            workflow = service.create_comprehensive_assessment_workflow(
                pilot_site=pilot,
                lat=0.0,
                lon=0.0
            )
            assert workflow["workflow_id"] is not None
    
    def test_cross_domain_workflow(self):
        """تست گردش کار بین دامنه‌ای"""
        engine = CouplingEngine()
        workflow = engine.create_workflow("Cross-Domain Test", "dishmok")
        
        # افزودن گام‌ها از دامنه‌های مختلف
        domains = ["drought", "soil_water", "financial", "iot", "hydrology"]
        
        for domain in domains:
            engine.add_step(
                workflow.workflow_id,
                domain=domain,
                service=f"{domain.capitalize()}Service",
                method="test_method"
            )
        
        result = engine.execute_workflow(workflow.workflow_id)
        
        assert result["status"] == "completed"
        assert result["total_steps"] == 5
