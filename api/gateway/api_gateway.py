"""API Gateway - Unified Entry Point

این ماژول یک نقطه ورود یکپارچه برای تمام APIها فراهم می‌کند
و درخواست‌ها را به سرویس‌های مناسب هدایت می‌نماید.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel


router = APIRouter(prefix="/gateway", tags=["Gateway"])


class UnifiedRequest(BaseModel):
    """درخواست یکپارچه"""
    domain: str
    service: str
    method: str
    parameters: Dict = {}
    pilot_site: Optional[str] = None


class WorkflowRequest(BaseModel):
    """درخواست ایجاد گردش کار"""
    name: str
    pilot_site: str
    steps: List[Dict]


class GatewayResponse(BaseModel):
    """پاسخ Gateway"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    timestamp: str


@router.get("/health")
async def health_check():
    """بررسی سلامت Gateway"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "domains": [
            "drought", "soil_water", "financial", "iot",
            "hydrology", "remote_sensing", "mrv", "dashboard",
            "training", "psychology"
        ]
    }


@router.get("/domains")
async def list_domains():
    """لیست تمام دامنه‌ها"""
    return {
        "domains": [
            {
                "name": "drought",
                "description": "مدیریت خشکسالی و پایش شاخص‌های آبی",
                "services": ["DroughtService"]
            },
            {
                "name": "soil_water",
                "description": "مدیریت خاک و آب",
                "services": ["SoilWaterService"]
            },
            {
                "name": "financial",
                "description": "مدیریت مالی و اقتصادی",
                "services": ["FinancialService"]
            },
            {
                "name": "iot",
                "description": "مدیریت دستگاه‌های IoT",
                "services": ["IoTService"]
            },
            {
                "name": "hydrology",
                "description": "مدل‌سازی هیدرولوژیک",
                "services": ["HydrologyService"]
            },
            {
                "name": "remote_sensing",
                "description": "سنجش‌ازدور و تحلیل تصاویر",
                "services": ["RemoteSensingService"]
            },
            {
                "name": "mrv",
                "description": "پایش، گزارش‌دهی و راستی‌آزمایی",
                "services": ["MRVService"]
            },
            {
                "name": "dashboard",
                "description": "داشبوردهای مدیریتی",
                "services": ["DashboardService"]
            },
            {
                "name": "training",
                "description": "آموزش و ظرفیت‌سازی",
                "services": ["TrainingService"]
            },
            {
                "name": "psychology",
                "description": "ارزیابی‌های روانشناختی",
                "services": ["PsychologyService"]
            }
        ]
    }


@router.post("/execute")
async def execute_unified_request(request: UnifiedRequest):
    """اجرای درخواست یکپارچه"""
    # در واقعیت باید به Coupling Engine متصل شود
    return GatewayResponse(
        success=True,
        data={
            "domain": request.domain,
            "service": request.service,
            "method": request.method,
            "result": "Executed successfully"
        },
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@router.post("/workflow/create")
async def create_workflow(request: WorkflowRequest):
    """ایجاد گردش کار جدید"""
    # در واقعیت باید به Coupling Engine متصل شود
    return GatewayResponse(
        success=True,
        data={
            "workflow_id": "wf_12345",
            "name": request.name,
            "pilot_site": request.pilot_site,
            "steps_count": len(request.steps)
        },
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@router.get("/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """دریافت وضعیت گردش کار"""
    return GatewayResponse(
        success=True,
        data={
            "workflow_id": workflow_id,
            "status": "completed",
            "steps_completed": 5,
            "total_steps": 5
        },
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@router.get("/pilots")
async def list_pilots():
    """لیست تمام پایلوت‌های جهانی"""
    return {
        "pilots": [
            {"id": "dishmok", "country": "ایران", "continent": "آسیا", "climate": "کوهستان خشک"},
            {"id": "behbahan", "country": "ایران", "continent": "آسیا", "climate": "دشت شور"},
            {"id": "rodbar_talesh", "country": "ایران", "continent": "آسیا", "climate": "جنگل مرطوب"},
            {"id": "snow_mountain", "country": "ایران", "continent": "آسیا", "climate": "کوهستان برفی"},
            {"id": "ouarzazate", "country": "مراکش", "continent": "آفریقا", "climate": "بیابانی نیمه‌خشک"},
            {"id": "wadi_rum", "country": "اردن", "continent": "آسیا", "climate": "بیابانی"},
            {"id": "sahel_senegal", "country": "سنگال", "continent": "آفریقا", "climate": "نیمه‌خشک ساحلی"},
            {"id": "ethiopian_highlands", "country": "اتیوپی", "continent": "آفریقا", "climate": "کوهستانی"},
            {"id": "rajasthan", "country": "هند", "continent": "آسیا", "climate": "نیمه‌خشک گرم"},
            {"id": "outback_australia", "country": "استرالیا", "continent": "اقیانوسیه", "climate": "بیابانی"},
            {"id": "atacama_chile", "country": "شیلی", "continent": "آمریکای جنوبی", "climate": "فوق‌خشک"},
            {"id": "mongolian_steppe", "country": "مغولستان", "continent": "آسیا", "climate": "استپ خشک سرد"}
        ],
        "total": 12,
        "continents": ["آسیا", "آفریقا", "اقیانوسیه", "آمریکای جنوبی"]
    }
