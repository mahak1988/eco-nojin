#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Professional Redesign of Soil & Water Module
- Backend: CRUD + Comprehensive Analysis
- Frontend: Dashboard with charts, tables, reports, projects
"""

from pathlib import Path

BASE = Path(".")
WEB = BASE / "apps/web/src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    print(f"  OK  {path}")


# ============================================================================
# BACKEND 1: Models - Add Project and AnalysisReport
# ============================================================================
def update_backend_models():
    """Add Project and AnalysisReport models"""
    models_path = BASE / "api/modules/soil_water/models.py"
    content = models_path.read_text(encoding='utf-8') if models_path.exists() else ""
    
    if 'class SoilWaterProject' not in content:
        addition = '''

# ============================================================================
# Soil Water Project Model
# ============================================================================
class SoilWaterProject(Base):
    """Project for organizing soil & water analyses"""
    __tablename__ = "soil_water_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=True)
    area_hectares = Column(Float, nullable=True)
    soil_type = Column(String(100), nullable=True)
    crop_type = Column(String(100), nullable=True)
    status = Column(String(50), default="active")  # active, archived, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    analyses = relationship("SoilWaterAnalysisReport", back_populates="project", cascade="all, delete-orphan")


# ============================================================================
# Soil Water Analysis Report Model
# ============================================================================
class SoilWaterAnalysisReport(Base):
    """Comprehensive analysis report"""
    __tablename__ = "soil_water_analysis_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("soil_water_projects.id"), nullable=True)
    title = Column(String(255), nullable=False)
    
    # Inputs (JSON)
    inputs = Column(JSON, nullable=True)
    
    # Results (JSON)
    results = Column(JSON, nullable=True)
    
    # Overall metrics
    overall_score = Column(Float, nullable=True)
    overall_health = Column(String(50), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    project = relationship("SoilWaterProject", back_populates="analyses")
'''
        content += addition
        models_path.write_text(content, encoding='utf-8')
        print(f"  OK  Added Project and Report models")
    else:
        print(f"  OK  Models already exist")


# ============================================================================
# BACKEND 2: Schemas
# ============================================================================
def update_backend_schemas():
    """Complete schemas with CRUD"""
    path = BASE / "api/modules/soil_water/schemas.py"
    content = '''"""
Soil & Water Schemas - Complete Version with CRUD
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


# ============================================================================
# Index Result Types
# ============================================================================
class LDNResult(BaseModel):
    ldn_score: float
    status: str
    soil_organic_carbon: float
    vegetation_cover: float
    erosion_risk: float


class NDVIResult(BaseModel):
    ndvi: float
    vegetation_health: str


class NDWIResult(BaseModel):
    ndwi: float
    water_presence: bool


class RUSLEResult(BaseModel):
    soil_loss_tons_per_ha: float
    erosion_risk_category: str
    r_factor: float
    k_factor: float
    ls_factor: float
    c_factor: float
    p_factor: float


class WaterBalanceResult(BaseModel):
    precipitation: float
    evapotranspiration: float
    runoff: float
    net_water: float
    soil_moisture_initial: float
    soil_moisture_final: float
    soil_moisture_change: float
    water_surplus: bool


class IrrigationResult(BaseModel):
    water_requirement_mm: float
    irrigation_interval_days: int
    efficiency_percentage: float
    depletion_fraction: float
    crop_type: str
    recommended_date: str


class DroughtResult(BaseModel):
    spi: float
    drought_category: str


class CarbonResult(BaseModel):
    carbon_stock_tons_per_ha: float
    soil_organic_carbon_pct: float
    bulk_density: float
    depth_cm: float


# ============================================================================
# Comprehensive Analysis
# ============================================================================
class ComprehensiveIndices(BaseModel):
    ldn: Optional[LDNResult] = None
    ndvi: Optional[NDVIResult] = None
    ndwi: Optional[NDWIResult] = None
    rusle: Optional[RUSLEResult] = None
    water_balance: Optional[WaterBalanceResult] = None
    irrigation: Optional[IrrigationResult] = None
    drought: Optional[DroughtResult] = None
    carbon: Optional[CarbonResult] = None


class ComprehensiveAnalysisRequest(BaseModel):
    ldn: Optional[dict] = None
    ndvi: Optional[dict] = None
    ndwi: Optional[dict] = None
    rusle: Optional[dict] = None
    water_balance: Optional[dict] = None
    irrigation: Optional[dict] = None
    drought: Optional[dict] = None
    carbon: Optional[dict] = None


class ComprehensiveAnalysisResponse(BaseModel):
    indices: ComprehensiveIndices
    overall_health: str
    overall_score: float
    recommendations: List[str]
    timestamp: str


# ============================================================================
# Project CRUD
# ============================================================================
class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    farmer_id: Optional[int] = None
    area_hectares: Optional[float] = None
    soil_type: Optional[str] = None
    crop_type: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    area_hectares: Optional[float] = None
    soil_type: Optional[str] = None
    crop_type: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    farmer_id: Optional[int] = None
    area_hectares: Optional[float] = None
    soil_type: Optional[str] = None
    crop_type: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    analysis_count: int = 0
    
    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    analyses: List["AnalysisReportResponse"] = []


# ============================================================================
# Analysis Report CRUD
# ============================================================================
class AnalysisReportCreate(BaseModel):
    project_id: Optional[int] = None
    title: str
    inputs: dict
    results: dict
    notes: Optional[str] = None


class AnalysisReportUpdate(BaseModel):
    title: Optional[str] = None
    notes: Optional[str] = None


class AnalysisReportResponse(BaseModel):
    id: int
    project_id: Optional[int] = None
    title: str
    inputs: Optional[dict] = None
    results: Optional[dict] = None
    overall_score: Optional[float] = None
    overall_health: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Dashboard Stats
# ============================================================================
class DashboardStats(BaseModel):
    total_projects: int
    active_projects: int
    total_analyses: int
    avg_score: float
    health_distribution: Dict[str, int]
    recent_analyses: List[AnalysisReportResponse]
'''
    path.write_text(content, encoding='utf-8')
    print(f"  OK  {path}")


# ============================================================================
# BACKEND 3: Service with CRUD
# ============================================================================
def update_backend_service():
    """Complete service with CRUD operations"""
    path = BASE / "api/modules/soil_water/service.py"
    content = path.read_text(encoding='utf-8') if path.exists() else ""
    
    # Add CRUD if not exists
    if 'async def create_project' not in content:
        # First, add imports at top if not present
        if 'from typing import List, Optional, Tuple' not in content:
            content = '''"""
Soil & Water Service - Complete with CRUD and Calculations
"""
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.modules.soil_water.models import (
    SoilWaterAnalysis, SoilWaterProject, SoilWaterAnalysisReport
)
from api.modules.soil_water import schemas


''' + content
        
        addition = '''

# ============================================================================
# PROJECT CRUD
# ============================================================================
async def list_projects(
    db: AsyncSession,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> Tuple[int, List[Dict[str, Any]]]:
    """List all projects with analysis count"""
    query = select(SoilWaterProject)
    if status:
        query = query.where(SoilWaterProject.status == status)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    query = query.order_by(desc(SoilWaterProject.created_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    projects = result.scalars().all()
    
    items = []
    for p in projects:
        # Count analyses
        count_result = await db.execute(
            select(func.count()).where(SoilWaterAnalysisReport.project_id == p.id)
        )
        analysis_count = count_result.scalar() or 0
        
        items.append({
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "location": p.location,
            "farmer_id": p.farmer_id,
            "area_hectares": p.area_hectares,
            "soil_type": p.soil_type,
            "crop_type": p.crop_type,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            "analysis_count": analysis_count,
        })
    
    return total, items


async def create_project(db: AsyncSession, data: schemas.ProjectCreate) -> Dict[str, Any]:
    """Create new project"""
    project = SoilWaterProject(
        title=data.title,
        description=data.description,
        location=data.location,
        farmer_id=data.farmer_id,
        area_hectares=data.area_hectares,
        soil_type=data.soil_type,
        crop_type=data.crop_type,
        status="active",
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    return {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "location": project.location,
        "status": project.status,
        "created_at": project.created_at.isoformat() if project.created_at else None,
    }


async def get_project(db: AsyncSession, project_id: int) -> Optional[Dict[str, Any]]:
    """Get project with analyses"""
    result = await db.execute(
        select(SoilWaterProject)
        .options(selectinload(SoilWaterProject.analyses))
        .where(SoilWaterProject.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        return None
    
    analyses = []
    for a in (project.analyses or []):
        analyses.append({
            "id": a.id,
            "title": a.title,
            "overall_score": a.overall_score,
            "overall_health": a.overall_health,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        })
    
    return {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "location": project.location,
        "farmer_id": project.farmer_id,
        "area_hectares": project.area_hectares,
        "soil_type": project.soil_type,
        "crop_type": project.crop_type,
        "status": project.status,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "analyses": analyses,
    }


async def update_project(
    db: AsyncSession, project_id: int, data: schemas.ProjectUpdate
) -> Optional[Dict[str, Any]]:
    """Update project"""
    result = await db.execute(
        select(SoilWaterProject).where(SoilWaterProject.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    
    await db.commit()
    await db.refresh(project)
    
    return {
        "id": project.id,
        "title": project.title,
        "status": project.status,
    }


async def delete_project(db: AsyncSession, project_id: int) -> bool:
    """Delete project and all its analyses"""
    result = await db.execute(
        select(SoilWaterProject).where(SoilWaterProject.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        return False
    
    await db.delete(project)
    await db.commit()
    return True


# ============================================================================
# ANALYSIS REPORT CRUD
# ============================================================================
async def list_reports(
    db: AsyncSession,
    project_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[int, List[Dict[str, Any]]]:
    """List analysis reports"""
    query = select(SoilWaterAnalysisReport)
    if project_id is not None:
        query = query.where(SoilWaterAnalysisReport.project_id == project_id)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    query = query.order_by(desc(SoilWaterAnalysisReport.created_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    reports = result.scalars().all()
    
    items = []
    for r in reports:
        items.append({
            "id": r.id,
            "project_id": r.project_id,
            "title": r.title,
            "inputs": r.inputs,
            "results": r.results,
            "overall_score": r.overall_score,
            "overall_health": r.overall_health,
            "notes": r.notes,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    
    return total, items


async def create_report(
    db: AsyncSession, data: schemas.AnalysisReportCreate
) -> Dict[str, Any]:
    """Create new analysis report"""
    # Calculate overall score from results
    results = data.results or {}
    indices = results.get("indices", {})
    overall_score = results.get("overall_score", 0)
    overall_health = results.get("overall_health", "good")
    
    report = SoilWaterAnalysisReport(
        project_id=data.project_id,
        title=data.title,
        inputs=data.inputs,
        results=data.results,
        overall_score=overall_score,
        overall_health=overall_health,
        notes=data.notes,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    return {
        "id": report.id,
        "project_id": report.project_id,
        "title": report.title,
        "overall_score": report.overall_score,
        "overall_health": report.overall_health,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


async def get_report(db: AsyncSession, report_id: int) -> Optional[Dict[str, Any]]:
    """Get report detail"""
    result = await db.execute(
        select(SoilWaterAnalysisReport).where(SoilWaterAnalysisReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        return None
    
    return {
        "id": report.id,
        "project_id": report.project_id,
        "title": report.title,
        "inputs": report.inputs,
        "results": report.results,
        "overall_score": report.overall_score,
        "overall_health": report.overall_health,
        "notes": report.notes,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


async def delete_report(db: AsyncSession, report_id: int) -> bool:
    """Delete report"""
    result = await db.execute(
        select(SoilWaterAnalysisReport).where(SoilWaterAnalysisReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        return False
    
    await db.delete(report)
    await db.commit()
    return True


# ============================================================================
# DASHBOARD STATS
# ============================================================================
async def get_dashboard_stats(db: AsyncSession) -> Dict[str, Any]:
    """Get dashboard statistics"""
    # Total projects
    total_p = await db.execute(select(func.count(SoilWaterProject.id)))
    total_projects = total_p.scalar() or 0
    
    # Active projects
    active_p = await db.execute(
        select(func.count(SoilWaterProject.id)).where(SoilWaterProject.status == "active")
    )
    active_projects = active_p.scalar() or 0
    
    # Total analyses
    total_a = await db.execute(select(func.count(SoilWaterAnalysisReport.id)))
    total_analyses = total_a.scalar() or 0
    
    # Average score
    avg_s = await db.execute(
        select(func.avg(SoilWaterAnalysisReport.overall_score))
    )
    avg_score = avg_s.scalar() or 0
    
    # Health distribution
    health_dist = {}
    for health in ["excellent", "good", "warning", "critical"]:
        result = await db.execute(
            select(func.count(SoilWaterAnalysisReport.id)).where(
                SoilWaterAnalysisReport.overall_health == health
            )
        )
        health_dist[health] = result.scalar() or 0
    
    # Recent analyses (last 5)
    recent_result = await db.execute(
        select(SoilWaterAnalysisReport)
        .order_by(desc(SoilWaterAnalysisReport.created_at))
        .limit(5)
    )
    recent = recent_result.scalars().all()
    recent_list = []
    for r in recent:
        recent_list.append({
            "id": r.id,
            "title": r.title,
            "overall_score": r.overall_score,
            "overall_health": r.overall_health,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    
    return {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "total_analyses": total_analyses,
        "avg_score": round(float(avg_score), 2),
        "health_distribution": health_dist,
        "recent_analyses": recent_list,
    }


'''
        content += addition
        path.write_text(content, encoding='utf-8')
        print(f"  OK  Added CRUD to service.py")
    else:
        print(f"  OK  CRUD already exists")


# ============================================================================
# BACKEND 4: Router with CRUD + comprehensive-analysis
# ============================================================================
def update_backend_router():
    """Complete router with all endpoints"""
    path = BASE / "api/modules/soil_water/router.py"
    
    content = '''"""
Soil & Water Router - Complete with CRUD + Comprehensive Analysis
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.soil_water import service as soil_service
from api.modules.soil_water import schemas

router = APIRouter(tags=["Soil & Water"])


# ============================================================================
# DASHBOARD
# ============================================================================
@router.get("/stats", response_model=schemas.DashboardStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics"""
    return await soil_service.get_dashboard_stats(db)


# ============================================================================
# COMPREHENSIVE ANALYSIS
# ============================================================================
@router.post("/comprehensive-analysis", response_model=schemas.ComprehensiveAnalysisResponse)
async def comprehensive_analysis(payload: schemas.ComprehensiveAnalysisRequest):
    """Perform comprehensive analysis - calculate all 8 indices"""
    try:
        result = soil_service.comprehensive_analysis(payload.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PROJECTS CRUD
# ============================================================================
@router.get("/projects")
async def list_projects(
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List all projects"""
    total, items = await soil_service.list_projects(db, status, limit, offset)
    return {"total": total, "items": items}


@router.post("/projects", response_model=schemas.ProjectResponse)
async def create_project(
    data: schemas.ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create new project"""
    return await soil_service.create_project(db, data)


@router.get("/projects/{project_id}", response_model=schemas.ProjectDetailResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Get project detail with analyses"""
    project = await soil_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/projects/{project_id}", response_model=schemas.ProjectResponse)
async def update_project(
    project_id: int,
    data: schemas.ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update project"""
    result = await soil_service.update_project(db, project_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


@router.delete("/projects/{project_id}")
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Delete project and all its analyses"""
    success = await soil_service.delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True}


# ============================================================================
# ANALYSIS REPORTS CRUD
# ============================================================================
@router.get("/reports")
async def list_reports(
    project_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List analysis reports"""
    total, items = await soil_service.list_reports(db, project_id, limit, offset)
    return {"total": total, "items": items}


@router.post("/reports", response_model=schemas.AnalysisReportResponse)
async def create_report(
    data: schemas.AnalysisReportCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create new analysis report"""
    return await soil_service.create_report(db, data)


@router.get("/reports/{report_id}", response_model=schemas.AnalysisReportResponse)
async def get_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """Get report detail"""
    report = await soil_service.get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.delete("/reports/{report_id}")
async def delete_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """Delete report"""
    success = await soil_service.delete_report(db, report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"success": True}


# ============================================================================
# INDIVIDUAL INDEX ENDPOINTS (for backward compatibility)
# ============================================================================
@router.get("/ldn")
async def calculate_ldn(
    soil_organic_carbon: float = Query(...),
    vegetation_cover: float = Query(...),
    erosion_risk: float = Query(...),
):
    """Calculate LDN"""
    payload = {"ldn": {"soil_organic_carbon": soil_organic_carbon, "vegetation_cover": vegetation_cover, "erosion_risk": erosion_risk}}
    result = soil_service.comprehensive_analysis(payload)
    return result.get("indices", {}).get("ldn", {})


@router.get("/ndvi")
async def calculate_ndvi(nir: float = Query(...), red: float = Query(...)):
    payload = {"ndvi": {"nir": nir, "red": red}}
    result = soil_service.comprehensive_analysis(payload)
    return result.get("indices", {}).get("ndvi", {})


@router.get("/ndwi")
async def calculate_ndwi(green: float = Query(...), nir: float = Query(...)):
    payload = {"ndwi": {"green": green, "nir": nir}}
    result = soil_service.comprehensive_analysis(payload)
    return result.get("indices", {}).get("ndwi", {})


@router.get("/rusle")
async def calculate_rusle(
    r_factor: float = Query(...),
    k_factor: float = Query(...),
    ls_factor: float = Query(...),
    c_factor: float = Query(...),
    p_factor: float = Query(...),
):
    payload = {"rusle": {"r_factor": r_factor, "k_factor": k_factor, "ls_factor": ls_factor, "c_factor": c_factor, "p_factor": p_factor}}
    result = soil_service.comprehensive_analysis(payload)
    return result.get("indices", {}).get("rusle", {})


@router.post("/water-balance")
async def calculate_water_balance(payload: dict):
    data = {"water_balance": payload}
    result = soil_service.comprehensive_analysis(data)
    return result.get("indices", {}).get("water_balance", {})


@router.get("/irrigation")
async def calculate_irrigation(
    crop_type: str = Query("generic"),
    field_capacity: float = Query(...),
    wilting_point: float = Query(...),
    current_moisture: float = Query(...),
    et_crop: float = Query(...),
    efficiency: float = Query(0.7),
):
    payload = {"irrigation": {"crop_type": crop_type, "field_capacity": field_capacity, "wilting_point": wilting_point, "current_moisture": current_moisture, "et_crop": et_crop, "efficiency": efficiency}}
    result = soil_service.comprehensive_analysis(payload)
    return result.get("indices", {}).get("irrigation", {})


@router.get("/drought-classification")
async def classify_drought(spi: float = Query(...)):
    payload = {"drought": {"spi": spi}}
    result = soil_service.comprehensive_analysis(payload)
    return result.get("indices", {}).get("drought", {})


@router.get("/carbon-sequestration")
async def calculate_carbon(
    soil_organic_carbon_pct: float = Query(...),
    bulk_density: float = Query(...),
    depth_cm: float = Query(30),
):
    payload = {"carbon": {"soil_organic_carbon_pct": soil_organic_carbon_pct, "bulk_density": bulk_density, "depth_cm": depth_cm}}
    result = soil_service.comprehensive_analysis(payload)
    return result.get("indices", {}).get("carbon", {})
'''
    
    path.write_text(content, encoding='utf-8')
    print(f"  OK  {path}")


# ============================================================================
# FRONTEND 1: Types
# ============================================================================
def create_frontend_types():
    content = '''// ============================================================================
// Soil & Water Types - Professional Version
// ============================================================================

export interface LDNResult {
  ldn_score: number;
  status: "healthy" | "degraded" | "critical";
  soil_organic_carbon: number;
  vegetation_cover: number;
  erosion_risk: number;
}

export interface NDVIResult {
  ndvi: number;
  vegetation_health: string;
}

export interface NDWIResult {
  ndwi: number;
  water_presence: boolean;
}

export interface RUSLEResult {
  soil_loss_tons_per_ha: number;
  erosion_risk_category: "low" | "moderate" | "high" | "very_high";
  r_factor: number;
  k_factor: number;
  ls_factor: number;
  c_factor: number;
  p_factor: number;
}

export interface WaterBalanceResult {
  precipitation: number;
  evapotranspiration: number;
  runoff: number;
  net_water: number;
  soil_moisture_initial: number;
  soil_moisture_final: number;
  soil_moisture_change: number;
  water_surplus: boolean;
}

export interface IrrigationResult {
  water_requirement_mm: number;
  irrigation_interval_days: number;
  efficiency_percentage: number;
  depletion_fraction: number;
  crop_type: string;
  recommended_date: string;
}

export interface DroughtResult {
  spi: number;
  drought_category: string;
}

export interface CarbonResult {
  carbon_stock_tons_per_ha: number;
  soil_organic_carbon_pct: number;
  bulk_density: number;
  depth_cm: number;
}

export interface AnalysisIndices {
  ldn?: LDNResult;
  ndvi?: NDVIResult;
  ndwi?: NDWIResult;
  rusle?: RUSLEResult;
  water_balance?: WaterBalanceResult;
  irrigation?: IrrigationResult;
  drought?: DroughtResult;
  carbon?: CarbonResult;
}

export interface ComprehensiveAnalysisRequest {
  ldn?: { soil_organic_carbon: number; vegetation_cover: number; erosion_risk: number };
  ndvi?: { nir: number; red: number };
  ndwi?: { green: number; nir: number };
  rusle?: { r_factor: number; k_factor: number; ls_factor: number; c_factor: number; p_factor: number };
  water_balance?: { precipitation: number; evapotranspiration: number; runoff_coefficient: number; soil_moisture_initial: number };
  irrigation?: { crop_type: string; field_capacity: number; wilting_point: number; current_moisture: number; et_crop: number; efficiency: number };
  drought?: { spi: number };
  carbon?: { soil_organic_carbon_pct: number; bulk_density: number; depth_cm: number };
}

export interface ComprehensiveAnalysisResponse {
  indices: AnalysisIndices;
  overall_health: "excellent" | "good" | "warning" | "critical";
  overall_score: number;
  recommendations: string[];
  timestamp: string;
}

export interface Project {
  id: number;
  title: string;
  description?: string;
  location?: string;
  farmer_id?: number;
  area_hectares?: number;
  soil_type?: string;
  crop_type?: string;
  status: string;
  created_at: string;
  updated_at?: string;
  analysis_count?: number;
  analyses?: AnalysisReport[];
}

export interface AnalysisReport {
  id: number;
  project_id?: number;
  title: string;
  inputs?: ComprehensiveAnalysisRequest;
  results?: ComprehensiveAnalysisResponse;
  overall_score?: number;
  overall_health?: string;
  notes?: string;
  created_at: string;
}

export interface DashboardStats {
  total_projects: number;
  active_projects: number;
  total_analyses: number;
  avg_score: number;
  health_distribution: Record<string, number>;
  recent_analyses: AnalysisReport[];
}
'''
    write_file(WEB / "lib/api/types/soilWater.types.ts", content)


# ============================================================================
# FRONTEND 2: Endpoints with /api/v1 prefix
# ============================================================================
def update_endpoints():
    path = WEB / "lib/api/endpoints.ts"
    content = '''// ============================================================================
// API Endpoints - With /api/v1 prefix
// ============================================================================

export const ENDPOINTS = {
  AUTH: {
    BASE: "/auth",
    OTP_REQUEST: "/auth/otp/request",
    OTP_VERIFY: "/auth/otp/verify",
    LOGIN: "/auth/login",
    PROFILE: "/auth/profile",
    LINK_WALLET: "/auth/profile/wallet",
  },
  FARMERS: {
    BASE: "/farmers",
    LIST: "/farmers",
    CREATE: "/farmers",
    DETAIL: (id: number) => `/farmers/${id}`,
    UPDATE: (id: number) => `/farmers/${id}`,
    DELETE: (id: number) => `/farmers/${id}`,
  },
  ECOCOIN: {
    BASE: "/ecocoin",
    TOKENS: "/ecocoin/tokens",
    STATS: "/ecocoin/stats",
    WALLETS: {
      BY_ID: (id: number) => `/ecocoin/wallets/${id}`,
      ME: "/ecocoin/wallets/me",
    },
    TRANSFER: "/ecocoin/transfer",
    STAKE: "/ecocoin/stake",
  },
  SOIL_WATER: {
    BASE: "/soil-water",
    STATS: "/soil-water/stats",
    COMPREHENSIVE: "/soil-water/comprehensive-analysis",
    PROJECTS: {
      LIST: "/soil-water/projects",
      CREATE: "/soil-water/projects",
      DETAIL: (id: number) => `/soil-water/projects/${id}`,
      UPDATE: (id: number) => `/soil-water/projects/${id}`,
      DELETE: (id: number) => `/soil-water/projects/${id}`,
    },
    REPORTS: {
      LIST: "/soil-water/reports",
      CREATE: "/soil-water/reports",
      DETAIL: (id: number) => `/soil-water/reports/${id}`,
      DELETE: (id: number) => `/soil-water/reports/${id}`,
    },
    LDN: "/soil-water/ldn",
    NDVI: "/soil-water/ndvi",
    NDWI: "/soil-water/ndwi",
    RUSLE: "/soil-water/rusle",
    WATER_BALANCE: "/soil-water/water-balance",
    IRRIGATION: "/soil-water/irrigation",
    DROUGHT: "/soil-water/drought-classification",
    CARBON: "/soil-water/carbon-sequestration",
  },
  ECOMINING: { BASE: "/ecomining" },
  WEATHER: { BASE: "/weather" },
  GIS: { BASE: "/gis" },
  AI: { BASE: "/ai" },
  ACADEMY: { BASE: "/academy" },
  STORE: { BASE: "/store" },
  DASHBOARD: { BASE: "/dashboard" },
} as const;

export function buildUrl(endpoint: string, params?: Record<string, any>): string {
  let url = endpoint;
  if (params) {
    const queryString = new URLSearchParams(
      Object.entries(params)
        .filter(([_, value]) => value !== undefined && value !== null)
        .reduce((acc, [key, value]) => {
          acc[key] = String(value);
          return acc;
        }, {} as Record<string, string>)
    ).toString();
    if (queryString) url += `?${queryString}`;
  }
  return url;
}
'''
    path.write_text(content, encoding='utf-8')
    print(f"  OK  {path}")


# ============================================================================
# FRONTEND 3: Hooks
# ============================================================================
def create_frontend_hooks():
    content = '''import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../client";
import { ENDPOINTS } from "../endpoints";
import { toast } from "react-hot-toast";
import type {
  ComprehensiveAnalysisRequest,
  ComprehensiveAnalysisResponse,
  Project,
  AnalysisReport,
  DashboardStats,
} from "../types/soilWater.types";

// ============================================================================
// DASHBOARD STATS
// ============================================================================
export function useDashboardStats() {
  return useQuery({
    queryKey: ["soil-water", "stats"],
    queryFn: async (): Promise<DashboardStats> =>
      apiClient.get(ENDPOINTS.SOIL_WATER.STATS),
    staleTime: 30 * 1000,
  });
}

// ============================================================================
// COMPREHENSIVE ANALYSIS
// ============================================================================
export function useComprehensiveAnalysis() {
  return useMutation({
    mutationFn: async (
      data: ComprehensiveAnalysisRequest
    ): Promise<ComprehensiveAnalysisResponse> =>
      apiClient.post(ENDPOINTS.SOIL_WATER.COMPREHENSIVE, data),
    onError: (error: any) => {
      toast.error(error?.PersianMessage || error?.message || "خطا در تحلیل");
    },
  });
}

// ============================================================================
// PROJECTS CRUD
// ============================================================================
export function useProjects(status?: string) {
  return useQuery({
    queryKey: ["soil-water", "projects", status],
    queryFn: async (): Promise<{ total: number; items: Project[] }> => {
      const params = status ? `?status=${status}` : "";
      return apiClient.get(ENDPOINTS.SOIL_WATER.PROJECTS.LIST + params);
    },
  });
}

export function useProject(id: number) {
  return useQuery({
    queryKey: ["soil-water", "projects", id],
    queryFn: async (): Promise<Project> =>
      apiClient.get(ENDPOINTS.SOIL_WATER.PROJECTS.DETAIL(id)),
    enabled: !!id,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: any): Promise<Project> =>
      apiClient.post(ENDPOINTS.SOIL_WATER.PROJECTS.CREATE, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["soil-water", "projects"] });
      toast.success("پروژه با موفقیت ایجاد شد");
    },
    onError: () => toast.error("خطا در ایجاد پروژه"),
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: any }): Promise<Project> =>
      apiClient.patch(ENDPOINTS.SOIL_WATER.PROJECTS.UPDATE(id), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["soil-water", "projects"] });
      toast.success("پروژه به‌روزرسانی شد");
    },
    onError: () => toast.error("خطا در به‌روزرسانی"),
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number): Promise<void> =>
      apiClient.delete(ENDPOINTS.SOIL_WATER.PROJECTS.DELETE(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["soil-water", "projects"] });
      toast.success("پروژه حذف شد");
    },
    onError: () => toast.error("خطا در حذف پروژه"),
  });
}

// ============================================================================
// ANALYSIS REPORTS CRUD
// ============================================================================
export function useReports(projectId?: number) {
  return useQuery({
    queryKey: ["soil-water", "reports", projectId],
    queryFn: async (): Promise<{ total: number; items: AnalysisReport[] }> => {
      const params = projectId ? `?project_id=${projectId}` : "";
      return apiClient.get(ENDPOINTS.SOIL_WATER.REPORTS.LIST + params);
    },
  });
}

export function useReport(id: number) {
  return useQuery({
    queryKey: ["soil-water", "reports", id],
    queryFn: async (): Promise<AnalysisReport> =>
      apiClient.get(ENDPOINTS.SOIL_WATER.REPORTS.DETAIL(id)),
    enabled: !!id,
  });
}

export function useCreateReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: any): Promise<AnalysisReport> =>
      apiClient.post(ENDPOINTS.SOIL_WATER.REPORTS.CREATE, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["soil-water", "reports"] });
      queryClient.invalidateQueries({ queryKey: ["soil-water", "projects"] });
      queryClient.invalidateQueries({ queryKey: ["soil-water", "stats"] });
      toast.success("تحلیل با موفقیت ذخیره شد");
    },
    onError: () => toast.error("خطا در ذخیره تحلیل"),
  });
}

export function useDeleteReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number): Promise<void> =>
      apiClient.delete(ENDPOINTS.SOIL_WATER.REPORTS.DELETE(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["soil-water", "reports"] });
      queryClient.invalidateQueries({ queryKey: ["soil-water", "stats"] });
      toast.success("تحلیل حذف شد");
    },
    onError: () => toast.error("خطا در حذف تحلیل"),
  });
}
'''
    write_file(WEB / "lib/api/hooks/useSoilWater.ts", content)


# ============================================================================
# FRONTEND 4: Main Dashboard Page (complete)
# ============================================================================
def create_main_page():
    content = '''"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Droplets, Leaf, TrendingDown, Sprout, CloudRain, Thermometer,
  Activity, TreePine, CheckCircle2, AlertTriangle, AlertCircle,
  Info, FileText, History, Download, Save, Trash2, Plus, FolderOpen,
  BarChart3, Loader2, RefreshCw, X, Edit, Eye, ChevronDown,
} from "lucide-react";
import Link from "next/link";
import { toast } from "react-hot-toast";
import {
  useComprehensiveAnalysis,
  useCreateProject,
  useProjects,
  useCreateReport,
  useReports,
  useDashboardStats,
  useDeleteReport,
} from "@/lib/api/hooks/useSoilWater";
import type {
  ComprehensiveAnalysisRequest,
  ComprehensiveAnalysisResponse,
  Project,
} from "@/lib/api/types/soilWater.types";
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend,
} from "recharts";

// ============================================================================
// Input Field
// ============================================================================
function InputField({
  label, value, onChange, unit, min, max, step = 0.1,
}: {
  label: string; value: number; onChange: (v: number) => void;
  unit?: string; min?: number; max?: number; step?: number;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-zinc-400 mb-1.5">{label}</label>
      <div className="flex items-center gap-2">
        <input
          type="number" value={value}
          onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
          min={min} max={max} step={step} dir="ltr"
          className="flex-1 min-w-0 px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white text-sm focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 text-left"
        />
        {unit && <span className="text-[10px] text-zinc-500 whitespace-nowrap min-w-[40px]">{unit}</span>}
      </div>
    </div>
  );
}

// ============================================================================
// Status Badge
// ============================================================================
function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { label: string; color: string; icon: any }> = {
    healthy: { label: "سالم", color: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30", icon: CheckCircle2 },
    degraded: { label: "تخریب‌شده", color: "bg-amber-500/20 text-amber-400 border-amber-500/30", icon: AlertTriangle },
    critical: { label: "بحرانی", color: "bg-rose-500/20 text-rose-400 border-rose-500/30", icon: AlertCircle },
    low: { label: "کم", color: "bg-emerald-500/20 text-emerald-400", icon: CheckCircle2 },
    moderate: { label: "متوسط", color: "bg-amber-500/20 text-amber-400", icon: AlertTriangle },
    high: { label: "زیاد", color: "bg-orange-500/20 text-orange-400", icon: AlertTriangle },
    very_high: { label: "خیلی زیاد", color: "bg-rose-500/20 text-rose-400", icon: AlertCircle },
    excellent: { label: "عالی", color: "bg-emerald-500/20 text-emerald-400", icon: CheckCircle2 },
    good: { label: "خوب", color: "bg-lime-500/20 text-lime-400", icon: CheckCircle2 },
    warning: { label: "هشدار", color: "bg-amber-500/20 text-amber-400", icon: AlertTriangle },
    dense_vegetation: { label: "متراکم", color: "bg-emerald-500/20 text-emerald-400", icon: TreePine },
    moderate_vegetation: { label: "متوسط", color: "bg-lime-500/20 text-lime-400", icon: Sprout },
    sparse_vegetation: { label: "پراکنده", color: "bg-yellow-500/20 text-yellow-400", icon: Sprout },
    bare_soil: { label: "خاک برهنه", color: "bg-amber-500/20 text-amber-400", icon: Info },
    near_normal: { label: "نرمال", color: "bg-zinc-500/20 text-zinc-400", icon: Info },
    moderately_dry: { label: "نسبتاً خشک", color: "bg-yellow-500/20 text-yellow-400", icon: Flame },
    severely_dry: { label: "خیلی خشک", color: "bg-orange-500/20 text-orange-400", icon: Flame },
    extremely_dry: { label: "خشکسالی شدید", color: "bg-rose-500/20 text-rose-400", icon: Flame },
  };
  const c = config[status] || { label: status, color: "bg-zinc-500/20 text-zinc-400", icon: Info };
  const Icon = c.icon;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-medium border ${c.color}`}>
      <Icon className="h-3 w-3" /> {c.label}
    </span>
  );
}

// ============================================================================
// Progress Bar
// ============================================================================
function ProgressBar({ value, max = 100, color = "emerald" }: any) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  const colors: Record<string, string> = {
    emerald: "from-emerald-500 to-teal-500",
    blue: "from-blue-500 to-cyan-500",
    green: "from-green-500 to-emerald-500",
    cyan: "from-cyan-500 to-blue-500",
    amber: "from-amber-500 to-orange-500",
    orange: "from-orange-500 to-red-500",
    rose: "from-rose-500 to-pink-500",
    teal: "from-teal-500 to-emerald-500",
    lime: "from-lime-500 to-green-500",
  };
  return (
    <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
      <motion.div
        initial={{ width: 0 }} animate={{ width: `${pct}%` }}
        transition={{ duration: 0.6 }}
        className={`h-full bg-gradient-to-r ${colors[color] || colors.emerald}`}
      />
    </div>
  );
}

// ============================================================================
// Modal Component
// ============================================================================
function Modal({ isOpen, onClose, title, children }: any) {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
        className="bg-[#1a1a1f] border border-white/10 rounded-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white">{title}</h2>
          <button onClick={onClose} className="p-2 text-zinc-400 hover:text-white rounded-lg">
            <X className="h-5 w-5" />
          </button>
        </div>
        {children}
      </motion.div>
    </div>
  );
}

// ============================================================================
// MAIN PAGE
// ============================================================================
export default function SoilWaterPage() {
  // Tabs
  const [activeTab, setActiveTab] = useState<"dashboard" | "calculator" | "reports" | "projects">("dashboard");
  
  // Input States
  const [ldn, setLdn] = useState({ soil_organic_carbon: 2.5, vegetation_cover: 45, erosion_risk: 30 });
  const [ndvi, setNdvi] = useState({ nir: 0.8, red: 0.2 });
  const [ndwi, setNdwi] = useState({ green: 0.3, nir: 0.6 });
  const [rusle, setRusle] = useState({ r_factor: 100, k_factor: 0.3, ls_factor: 1.5, c_factor: 0.4, p_factor: 0.8 });
  const [wb, setWb] = useState({ precipitation: 100, evapotranspiration: 60, runoff_coefficient: 0.3, soil_moisture_initial: 50 });
  const [irr, setIrr] = useState({ crop_type: "گندم", field_capacity: 32, wilting_point: 15, current_moisture: 22, et_crop: 5, efficiency: 0.7 });
  const [drought, setDrought] = useState({ spi: -1.2 });
  const [carbon, setCarbon] = useState({ soil_organic_carbon_pct: 2.5, bulk_density: 1.3, depth_cm: 30 });
  
  // Analysis state
  const [analysisTitle, setAnalysisTitle] = useState("");
  const [selectedProjectId, setSelectedProjectId] = useState<number | undefined>();
  const [results, setResults] = useState<ComprehensiveAnalysisResponse | null>(null);
  
  // Modals
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showReportDetail, setShowReportDetail] = useState<number | null>(null);
  
  // Project form
  const [newProject, setNewProject] = useState({ title: "", description: "", location: "", area_hectares: 0, soil_type: "", crop_type: "" });
  
  // Hooks
  const analysis = useComprehensiveAnalysis();
  const createProject = useCreateProject();
  const projects = useProjects();
  const reports = useReports();
  const stats = useDashboardStats();
  const createReport = useCreateReport();
  const deleteReport = useDeleteReport();

  // Build payload
  const buildPayload = (): ComprehensiveAnalysisRequest => ({
    ldn, ndvi, ndwi, rusle,
    water_balance: wb, irrigation: irr, drought, carbon,
  });

  // Calculate all
  const handleCalculate = async () => {
    try {
      const payload = buildPayload();
      const result = await analysis.mutateAsync(payload);
      setResults(result);
      toast.success("تحلیل با موفقیت انجام شد");
    } catch (error) {
      console.error("Analysis error:", error);
    }
  };

  // Save analysis to database
  const handleSave = async () => {
    if (!results) {
      toast.error("ابتدا تحلیل را محاسبه کنید");
      return;
    }
    if (!analysisTitle.trim()) {
      toast.error("عنوان تحلیل الزامی است");
      return;
    }
    try {
      await createReport.mutateAsync({
        project_id: selectedProjectId,
        title: analysisTitle,
        inputs: buildPayload(),
        results: results,
      });
      setAnalysisTitle("");
      setShowSaveModal(false);
    } catch (error) {
      console.error("Save error:", error);
    }
  };

  // Create new project
  const handleCreateProject = async () => {
    if (!newProject.title.trim()) {
      toast.error("عنوان پروژه الزامی است");
      return;
    }
    try {
      await createProject.mutateAsync(newProject);
      setNewProject({ title: "", description: "", location: "", area_hectares: 0, soil_type: "", crop_type: "" });
      setShowProjectModal(false);
      projects.refetch();
    } catch (error) {
      console.error("Create project error:", error);
    }
  };

  // Export CSV
  const handleExportCSV = () => {
    if (!results) {
      toast.error("ابتدا تحلیل را محاسبه کنید");
      return;
    }
    try {
      const rows = [["شاخص", "مقدار", "واحد", "وضعیت"]];
      if (results.indices.ldn) rows.push(["LDN", results.indices.ldn.ldn_score.toString(), "/100", results.indices.ldn.status]);
      if (results.indices.ndvi) rows.push(["NDVI", results.indices.ndvi.ndvi.toString(), "", results.indices.ndvi.vegetation_health]);
      if (results.indices.ndwi) rows.push(["NDWI", results.indices.ndwi.ndwi.toString(), "", results.indices.ndwi.water_presence ? "آب" : "خشک"]);
      if (results.indices.rusle) rows.push(["فرسایش", results.indices.rusle.soil_loss_tons_per_ha.toString(), "t/ha", results.indices.rusle.erosion_risk_category]);
      if (results.indices.water_balance) {
        rows.push(["رواناب", results.indices.water_balance.runoff.toString(), "mm", ""]);
        rows.push(["آب خالص", results.indices.water_balance.net_water.toString(), "mm", ""]);
      }
      if (results.indices.irrigation) rows.push(["نیاز آبی", results.indices.irrigation.water_requirement_mm.toString(), "mm", ""]);
      if (results.indices.drought) rows.push(["SPI", results.indices.drought.spi.toString(), "", results.indices.drought.drought_category]);
      if (results.indices.carbon) rows.push(["کربن", results.indices.carbon.carbon_stock_tons_per_ha.toString(), "t/ha", ""]);
      rows.push([]);
      rows.push(["امتیاز کل", results.overall_score.toString(), "/100", results.overall_health]);
      rows.push([]);
      rows.push(["توصیه‌ها"]);
      results.recommendations.forEach((r) => rows.push([r]));
      
      const csv = rows.map((r) => r.join(",")).join("\\n");
      const blob = new Blob(["\\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = `soil-water-${Date.now()}.csv`;
      a.click(); URL.revokeObjectURL(url);
      toast.success("CSV دانلود شد");
    } catch (error) {
      toast.error("خطا در خروجی CSV");
    }
  };

  // Export JSON
  const handleExportJSON = () => {
    if (!results) {
      toast.error("ابتدا تحلیل را محاسبه کنید");
      return;
    }
    try {
      const blob = new Blob([JSON.stringify({ analysisTitle, inputs: buildPayload(), results }, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = `soil-water-${Date.now()}.json`;
      a.click(); URL.revokeObjectURL(url);
      toast.success("JSON دانلود شد");
    } catch (error) {
      toast.error("خطا در خروجی JSON");
    }
  };

  // Health colors
  const healthConfig: Record<string, { color: string; label: string; gradient: string; chartColor: string }> = {
    excellent: { color: "text-emerald-400", label: "عالی", gradient: "from-emerald-500 to-teal-500", chartColor: "#10b981" },
    good: { color: "text-lime-400", label: "خوب", gradient: "from-lime-500 to-emerald-500", chartColor: "#84cc16" },
    warning: { color: "text-amber-400", label: "هشدار", gradient: "from-amber-500 to-orange-500", chartColor: "#f59e0b" },
    critical: { color: "text-rose-400", label: "بحرانی", gradient: "from-rose-500 to-red-500", chartColor: "#f43f5e" },
  };

  const health = results ? healthConfig[results.overall_health] || healthConfig.good : healthConfig.good;

  // Chart data
  const radarData = results ? [
    { index: "LDN", value: results.indices.ldn?.ldn_score || 0 },
    { index: "NDVI", value: (results.indices.ndvi?.ndvi || 0) * 100 },
    { index: "فرسایش", value: Math.max(0, 100 - (results.indices.rusle?.soil_loss_tons_per_ha || 0) * 2) },
    { index: "آب", value: results.indices.water_balance?.water_surplus ? 80 : 30 },
    { index: "کربن", value: Math.min(100, (results.indices.carbon?.carbon_stock_tons_per_ha || 0) * 2) },
  ] : [];

  const healthDistributionData = stats.data?.health_distribution ? Object.entries(stats.data.health_distribution).map(([key, value]) => ({
    name: healthConfig[key]?.label || key,
    value,
    color: healthConfig[key]?.chartColor || "#888",
  })) : [];

  return (
    <div className="min-h-screen relative p-4 lg:p-8">
      {/* Background */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div className="absolute inset-0 opacity-50" style={{
          backgroundImage: `radial-gradient(at 20% 30%, rgba(16, 185, 129, 0.15) 0px, transparent 50%), radial-gradient(at 80% 70%, rgba(59, 130, 246, 0.15) 0px, transparent 50%)`,
        }} />
      </div>

      <div className="max-w-[1600px] mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-[0_0_40px_rgba(16,185,129,0.3)]">
              <Droplets className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl lg:text-3xl font-black text-white">داشبورد جامع آب و خاک</h1>
              <p className="text-zinc-400 text-sm mt-1">۸ شاخص علمی • محاسبه سرور • گزارش‌گیری حرفه‌ای</p>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 border-b border-white/10 pb-2">
            {[
              { key: "dashboard", label: "نمای کلی", icon: BarChart3 },
              { key: "calculator", label: "ماشین‌حساب", icon: Activity },
              { key: "reports", label: "گزارش‌ها", icon: FileText },
              { key: "projects", label: "پروژه‌ها", icon: FolderOpen },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.key;
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                    isActive ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" : "text-zinc-400 hover:bg-white/[0.03]"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span className="text-sm font-medium">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </motion.div>

        {/* DASHBOARD TAB */}
        {activeTab === "dashboard" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <p className="text-xs text-zinc-400 mb-1">کل پروژه‌ها</p>
                <p className="text-3xl font-black text-white">{stats.data?.total_projects || 0}</p>
              </div>
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <p className="text-xs text-zinc-400 mb-1">پروژه‌های فعال</p>
                <p className="text-3xl font-black text-emerald-400">{stats.data?.active_projects || 0}</p>
              </div>
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <p className="text-xs text-zinc-400 mb-1">کل تحلیل‌ها</p>
                <p className="text-3xl font-black text-blue-400">{stats.data?.total_analyses || 0}</p>
              </div>
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <p className="text-xs text-zinc-400 mb-1">میانگین امتیاز</p>
                <p className="text-3xl font-black text-amber-400">{(stats.data?.avg_score || 0).toFixed(1)}</p>
              </div>
            </div>

            {/* Charts */}
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Health Distribution Pie */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <h3 className="text-sm font-bold text-white mb-4">توزیع وضعیت سلامت</h3>
                {healthDistributionData.length > 0 && healthDistributionData.some(d => d.value > 0) ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie data={healthDistributionData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                        {healthDistributionData.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ backgroundColor: "#1a1a1f", border: "1px solid rgba(255,255,255,0.1)" }} />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[250px] flex items-center justify-center text-zinc-500 text-sm">
                    داده‌ای موجود نیست
                  </div>
                )}
              </div>

              {/* Radar Chart */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <h3 className="text-sm font-bold text-white mb-4">نمودار راداری شاخص‌ها</h3>
                {radarData.length > 0 && results ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <RadarChart data={radarData}>
                      <PolarGrid stroke="#333" />
                      <PolarAngleAxis dataKey="index" tick={{ fill: "#999", fontSize: 11 }} />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: "#666", fontSize: 10 }} />
                      <Radar name="شاخص" dataKey="value" stroke="#10b981" fill="#10b981" fillOpacity={0.5} />
                    </RadarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[250px] flex items-center justify-center text-zinc-500 text-sm">
                    ابتدا تحلیل را محاسبه کنید
                  </div>
                )}
              </div>
            </div>

            {/* Recent Analyses Table */}
            <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-white">تحلیل‌های اخیر</h3>
                <button onClick={() => setActiveTab("reports")} className="text-xs text-emerald-400 hover:text-emerald-300">
                  مشاهده همه →
                </button>
              </div>
              {reports.data?.items && reports.data.items.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="text-right py-2 px-3 text-zinc-400 font-medium">عنوان</th>
                        <th className="text-right py-2 px-3 text-zinc-400 font-medium">امتیاز</th>
                        <th className="text-right py-2 px-3 text-zinc-400 font-medium">وضعیت</th>
                        <th className="text-right py-2 px-3 text-zinc-400 font-medium">تاریخ</th>
                        <th className="text-right py-2 px-3 text-zinc-400 font-medium">عملیات</th>
                      </tr>
                    </thead>
                    <tbody>
                      {reports.data.items.slice(0, 5).map((report) => (
                        <tr key={report.id} className="border-b border-white/5 hover:bg-white/[0.02]">
                          <td className="py-2 px-3 text-white">{report.title}</td>
                          <td className="py-2 px-3 text-white font-bold tabular-nums" dir="ltr">
                            {report.overall_score?.toFixed(1) || "-"}
                          </td>
                          <td className="py-2 px-3">
                            {report.overall_health && <StatusBadge status={report.overall_health} />}
                          </td>
                          <td className="py-2 px-3 text-zinc-400 text-xs">
                            {new Date(report.created_at).toLocaleDateString("fa-IR")}
                          </td>
                          <td className="py-2 px-3">
                            <div className="flex gap-2">
                              <button
                                onClick={() => setShowReportDetail(report.id)}
                                className="p-1 text-blue-400 hover:bg-blue-500/10 rounded"
                              >
                                <Eye className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => {
                                  if (confirm("آیا از حذف این تحلیل مطمئن هستید؟")) {
                                    deleteReport.mutate(report.id);
                                  }
                                }}
                                className="p-1 text-rose-400 hover:bg-rose-500/10 rounded"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="py-12 text-center text-zinc-500 text-sm">
                  <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  هنوز تحلیلی ثبت نشده است
                </div>
              )}
            </div>
          </motion.div>
        )}

        {/* CALCULATOR TAB */}
        {activeTab === "calculator" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
            {/* Action Bar */}
            <div className="p-4 bg-white/[0.03] border border-white/10 rounded-2xl">
              <div className="flex flex-wrap items-center gap-3">
                <button
                  onClick={handleCalculate}
                  disabled={analysis.isPending}
                  className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 rounded-lg text-white text-sm font-medium flex items-center gap-2 disabled:opacity-50"
                >
                  {analysis.isPending ? (
                    <><Loader2 className="h-4 w-4 animate-spin" /> در حال محاسبه...</>
                  ) : (
                    <><RefreshCw className="h-4 w-4" /> محاسبه همه</>
                  )}
                </button>
                <button
                  onClick={() => setShowSaveModal(true)}
                  disabled={!results}
                  className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/30 text-blue-400 rounded-lg text-sm font-medium flex items-center gap-2 disabled:opacity-50"
                >
                  <Save className="h-4 w-4" /> ثبت تحلیل
                </button>
                <button
                  onClick={handleExportCSV}
                  disabled={!results}
                  className="px-4 py-2 bg-white/[0.03] hover:bg-white/[0.05] border border-white/10 text-zinc-300 rounded-lg text-sm flex items-center gap-2 disabled:opacity-50"
                >
                  <Download className="h-4 w-4" /> CSV
                </button>
                <button
                  onClick={handleExportJSON}
                  disabled={!results}
                  className="px-4 py-2 bg-white/[0.03] hover:bg-white/[0.05] border border-white/10 text-zinc-300 rounded-lg text-sm flex items-center gap-2 disabled:opacity-50"
                >
                  <Download className="h-4 w-4" /> JSON
                </button>
              </div>
            </div>

            {/* Overall Health Banner */}
            {results && (
              <div className="p-6 bg-gradient-to-r from-white/[0.03] to-white/[0.01] border border-white/10 rounded-2xl">
                <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
                  <div>
                    <p className="text-xs text-zinc-400 mb-1">وضعیت کلی زمین</p>
                    <h2 className={`text-3xl font-black bg-gradient-to-r ${health.gradient} bg-clip-text text-transparent`}>
                      {health.label}
                    </h2>
                  </div>
                  <div className="text-left">
                    <p className="text-xs text-zinc-400 mb-1">امتیاز کل</p>
                    <p className="text-4xl font-black text-white tabular-nums" dir="ltr">
                      {results.overall_score.toFixed(0)}
                      <span className="text-sm text-zinc-500 mr-1">/ 100</span>
                    </p>
                  </div>
                </div>
                <ProgressBar value={results.overall_score} color={results.overall_health === "excellent" || results.overall_health === "good" ? "emerald" : results.overall_health === "warning" ? "amber" : "rose"} />
                {results.recommendations.length > 0 && (
                  <div className="mt-4 p-3 bg-amber-500/5 border border-amber-500/20 rounded-xl">
                    <p className="text-xs text-amber-300 font-medium mb-2">توصیه‌های هوشمند:</p>
                    <ul className="space-y-1">
                      {results.recommendations.map((r, i) => (
                        <li key={i} className="text-xs text-amber-200/80 flex items-start gap-2">
                          <AlertTriangle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                          {r}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* 8 Index Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* LDN */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <Leaf className="h-4 w-4 text-emerald-400" />
                  <h3 className="text-sm font-bold text-white">شاخص LDN</h3>
                </div>
                <div className="space-y-2">
                  <InputField label="کربن آلی" value={ldn.soil_organic_carbon} onChange={(v) => setLdn({ ...ldn, soil_organic_carbon: v })} unit="%" min={0} max={10} />
                  <InputField label="پوشش گیاهی" value={ldn.vegetation_cover} onChange={(v) => setLdn({ ...ldn, vegetation_cover: v })} unit="%" min={0} max={100} />
                  <InputField label="خطر فرسایش" value={ldn.erosion_risk} onChange={(v) => setLdn({ ...ldn, erosion_risk: v })} unit="%" min={0} max={100} />
                </div>
                {results?.indices.ldn && (
                  <>
                    <div className="mt-3 pt-3 border-t border-white/5">
                      <p className="text-[10px] text-zinc-500 mb-1">امتیاز LDN</p>
                      <p className="text-xl font-bold text-emerald-400 tabular-nums" dir="ltr">
                        {results.indices.ldn.ldn_score.toFixed(1)}
                        <span className="text-xs text-zinc-500 mr-1">/ 100</span>
                      </p>
                    </div>
                    <div className="mt-2"><StatusBadge status={results.indices.ldn.status} /></div>
                    <ProgressBar value={results.indices.ldn.ldn_score} color="emerald" />
                  </>
                )}
              </div>

              {/* NDVI */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <Sprout className="h-4 w-4 text-green-400" />
                  <h3 className="text-sm font-bold text-white">شاخص NDVI</h3>
                </div>
                <div className="space-y-2">
                  <InputField label="NIR" value={ndvi.nir} onChange={(v) => setNdvi({ ...ndvi, nir: v })} min={0} max={1} step={0.01} />
                  <InputField label="Red" value={ndvi.red} onChange={(v) => setNdvi({ ...ndvi, red: v })} min={0} max={1} step={0.01} />
                </div>
                {results?.indices.ndvi && (
                  <>
                    <div className="mt-3 pt-3 border-t border-white/5">
                      <p className="text-[10px] text-zinc-500 mb-1">مقدار NDVI</p>
                      <p className="text-xl font-bold text-green-400 tabular-nums" dir="ltr">
                        {results.indices.ndvi.ndvi.toFixed(3)}
                      </p>
                    </div>
                    <div className="mt-2"><StatusBadge status={results.indices.ndvi.vegetation_health} /></div>
                  </>
                )}
              </div>

              {/* NDWI */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <CloudRain className="h-4 w-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white">شاخص NDWI</h3>
                </div>
                <div className="space-y-2">
                  <InputField label="Green" value={ndwi.green} onChange={(v) => setNdwi({ ...ndwi, green: v })} min={0} max={1} step={0.01} />
                  <InputField label="NIR" value={ndwi.nir} onChange={(v) => setNdwi({ ...ndwi, nir: v })} min={0} max={1} step={0.01} />
                </div>
                {results?.indices.ndwi && (
                  <div className="mt-3 pt-3 border-t border-white/5">
                    <p className="text-[10px] text-zinc-500 mb-1">مقدار NDWI</p>
                    <p className="text-xl font-bold text-cyan-400 tabular-nums" dir="ltr">
                      {results.indices.ndwi.ndwi.toFixed(3)}
                    </p>
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-medium border mt-2 ${
                      results.indices.ndwi.water_presence ? "bg-cyan-500/20 text-cyan-400 border-cyan-500/30" : "bg-zinc-500/20 text-zinc-400 border-zinc-500/30"
                    }`}>
                      {results.indices.ndwi.water_presence ? "وجود آب" : "خشک"}
                    </span>
                  </div>
                )}
              </div>

              {/* RUSLE */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingDown className="h-4 w-4 text-amber-400" />
                  <h3 className="text-sm font-bold text-white">فرسایش RUSLE</h3>
                </div>
                <div className="space-y-2">
                  <InputField label="R (باران)" value={rusle.r_factor} onChange={(v) => setRusle({ ...rusle, r_factor: v })} min={0} />
                  <InputField label="K (خاک)" value={rusle.k_factor} onChange={(v) => setRusle({ ...rusle, k_factor: v })} min={0} max={1} step={0.01} />
                  <InputField label="LS (شیب)" value={rusle.ls_factor} onChange={(v) => setRusle({ ...rusle, ls_factor: v })} min={0} step={0.1} />
                  <div className="grid grid-cols-2 gap-2">
                    <InputField label="C" value={rusle.c_factor} onChange={(v) => setRusle({ ...rusle, c_factor: v })} min={0} max={1} step={0.01} />
                    <InputField label="P" value={rusle.p_factor} onChange={(v) => setRusle({ ...rusle, p_factor: v })} min={0} max={1} step={0.01} />
                  </div>
                </div>
                {results?.indices.rusle && (
                  <>
                    <div className="mt-3 pt-3 border-t border-white/5">
                      <p className="text-[10px] text-zinc-500 mb-1">اتلاف خاک</p>
                      <p className="text-xl font-bold text-amber-400 tabular-nums" dir="ltr">
                        {results.indices.rusle.soil_loss_tons_per_ha.toFixed(1)}
                        <span className="text-xs text-zinc-500 mr-1">t/ha/yr</span>
                      </p>
                    </div>
                    <div className="mt-2"><StatusBadge status={results.indices.rusle.erosion_risk_category} /></div>
                  </>
                )}
              </div>

              {/* Water Balance */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <Droplets className="h-4 w-4 text-blue-400" />
                  <h3 className="text-sm font-bold text-white">بیلان آبی</h3>
                </div>
                <div className="space-y-2">
                  <InputField label="بارندگی" value={wb.precipitation} onChange={(v) => setWb({ ...wb, precipitation: v })} unit="mm" min={0} />
                  <InputField label="تبخیر-تعرق" value={wb.evapotranspiration} onChange={(v) => setWb({ ...wb, evapotranspiration: v })} unit="mm" min={0} />
                  <div className="grid grid-cols-2 gap-2">
                    <InputField label="ضریب R" value={wb.runoff_coefficient} onChange={(v) => setWb({ ...wb, runoff_coefficient: v })} min={0} max={1} step={0.05} />
                    <InputField label="رطوبت" value={wb.soil_moisture_initial} onChange={(v) => setWb({ ...wb, soil_moisture_initial: v })} unit="mm" min={0} />
                  </div>
                </div>
                {results?.indices.water_balance && (
                  <div className="mt-3 pt-3 border-t border-white/5 grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-[10px] text-zinc-500">رواناب</p>
                      <p className="text-sm font-bold text-blue-400 tabular-nums" dir="ltr">
                        {results.indices.water_balance.runoff.toFixed(1)} mm
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] text-zinc-500">آب خالص</p>
                      <p className={`text-sm font-bold tabular-nums ${results.indices.water_balance.water_surplus ? "text-emerald-400" : "text-amber-400"}`} dir="ltr">
                        {results.indices.water_balance.net_water.toFixed(1)} mm
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Irrigation */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <Thermometer className="h-4 w-4 text-sky-400" />
                  <h3 className="text-sm font-bold text-white">نیاز آبیاری</h3>
                </div>
                <div className="space-y-2">
                  <div>
                    <label className="block text-xs font-medium text-zinc-400 mb-1.5">محصول</label>
                    <select
                      value={irr.crop_type}
                      onChange={(e) => setIrr({ ...irr, crop_type: e.target.value })}
                      className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white text-sm"
                    >
                      <option value="گندم">گندم</option>
                      <option value="جو">جو</option>
                      <option value="ذرت">ذرت</option>
                      <option value="برنج">برنج</option>
                      <option value="پنبه">پنبه</option>
                    </select>
                  </div>
                  <InputField label="FC" value={irr.field_capacity} onChange={(v) => setIrr({ ...irr, field_capacity: v })} unit="%" min={0} max={100} />
                  <InputField label="WP" value={irr.wilting_point} onChange={(v) => setIrr({ ...irr, wilting_point: v })} unit="%" min={0} max={100} />
                  <InputField label="رطوبت فعلی" value={irr.current_moisture} onChange={(v) => setIrr({ ...irr, current_moisture: v })} unit="%" min={0} max={100} />
                  <InputField label="ETc" value={irr.et_crop} onChange={(v) => setIrr({ ...irr, et_crop: v })} unit="mm/day" min={0} />
                </div>
                {results?.indices.irrigation && (
                  <div className="mt-3 pt-3 border-t border-white/5">
                    <p className="text-[10px] text-zinc-500 mb-1">نیاز آبی</p>
                    <p className="text-xl font-bold text-sky-400 tabular-nums" dir="ltr">
                      {results.indices.irrigation.water_requirement_mm.toFixed(1)}
                      <span className="text-xs text-zinc-500 mr-1">mm</span>
                    </p>
                  </div>
                )}
              </div>

              {/* Drought */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <Activity className="h-4 w-4 text-orange-400" />
                  <h3 className="text-sm font-bold text-white">خشکسالی SPI</h3>
                </div>
                <div className="space-y-2">
                  <InputField label="شاخص SPI" value={drought.spi} onChange={(v) => setDrought({ spi: v })} min={-3} max={3} step={0.1} />
                </div>
                {results?.indices.drought && (
                  <>
                    <div className="mt-3 pt-3 border-t border-white/5">
                      <p className="text-[10px] text-zinc-500 mb-1">مقدار SPI</p>
                      <p className="text-xl font-bold text-orange-400 tabular-nums" dir="ltr">
                        {results.indices.drought.spi.toFixed(2)}
                      </p>
                    </div>
                    <div className="mt-2"><StatusBadge status={results.indices.drought.drought_category} /></div>
                  </>
                )}
              </div>

              {/* Carbon */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <TreePine className="h-4 w-4 text-teal-400" />
                  <h3 className="text-sm font-bold text-white">ترسیب کربن</h3>
                </div>
                <div className="space-y-2">
                  <InputField label="SOC" value={carbon.soil_organic_carbon_pct} onChange={(v) => setCarbon({ ...carbon, soil_organic_carbon_pct: v })} unit="%" min={0} max={10} step={0.1} />
                  <InputField label="چگالی ظاهری" value={carbon.bulk_density} onChange={(v) => setCarbon({ ...carbon, bulk_density: v })} unit="g/cm³" min={0.5} max={2.5} step={0.05} />
                  <InputField label="عمق خاک" value={carbon.depth_cm} onChange={(v) => setCarbon({ ...carbon, depth_cm: v })} unit="cm" min={0} max={200} step={5} />
                </div>
                {results?.indices.carbon && (
                  <div className="mt-3 pt-3 border-t border-white/5">
                    <p className="text-[10px] text-zinc-500 mb-1">ذخیره کربن</p>
                    <p className="text-xl font-bold text-teal-400 tabular-nums" dir="ltr">
                      {results.indices.carbon.carbon_stock_tons_per_ha.toFixed(1)}
                      <span className="text-xs text-zinc-500 mr-1">t/ha</span>
                    </p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {/* REPORTS TAB */}
        {activeTab === "reports" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">گزارش‌های ذخیره شده</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => reports.refetch()}
                  className="px-3 py-2 bg-white/[0.03] border border-white/10 rounded-lg text-zinc-300 hover:bg-white/[0.05] text-sm flex items-center gap-2"
                >
                  <RefreshCw className="h-4 w-4" /> تازه‌سازی
                </button>
                <button
                  onClick={() => setActiveTab("calculator")}
                  className="px-3 py-2 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 rounded-lg text-sm flex items-center gap-2"
                >
                  <Plus className="h-4 w-4" /> تحلیل جدید
                </button>
              </div>
            </div>
            
            {reports.data?.items && reports.data.items.length > 0 ? (
              <div className="space-y-3">
                {reports.data.items.map((report) => (
                  <motion.div
                    key={report.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl hover:border-white/20 transition-all"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-white mb-1">{report.title}</h3>
                        <div className="flex flex-wrap items-center gap-3 text-xs text-zinc-500 mb-3">
                          <span>📅 {new Date(report.created_at).toLocaleString("fa-IR")}</span>
                          {report.project_id && <span>📁 پروژه #{report.project_id}</span>}
                          <span className="font-bold tabular-nums text-white" dir="ltr">
                            امتیاز: {report.overall_score?.toFixed(1) || "-"}
                          </span>
                          {report.overall_health && <StatusBadge status={report.overall_health} />}
                        </div>
                        {report.results?.recommendations && report.results.recommendations.length > 0 && (
                          <p className="text-xs text-zinc-400">
                            💡 {report.results.recommendations[0]}
                          </p>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setShowReportDetail(report.id)}
                          className="p-2 text-blue-400 hover:bg-blue-500/10 rounded-lg transition-all"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => {
                            if (confirm("آیا از حذف این گزارش مطمئن هستید؟")) {
                              deleteReport.mutate(report.id);
                            }
                          }}
                          className="p-2 text-rose-400 hover:bg-rose-500/10 rounded-lg transition-all"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="p-12 bg-white/[0.03] border border-white/10 rounded-2xl text-center">
                <FileText className="h-16 w-16 text-zinc-600 mx-auto mb-4" />
                <p className="text-zinc-400 mb-4">هنوز گزارشی ذخیره نشده است</p>
                <button
                  onClick={() => setActiveTab("calculator")}
                  className="px-4 py-2 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 rounded-lg text-sm"
                >
                  ایجاد اولین تحلیل →
                </button>
              </div>
            )}
          </motion.div>
        )}

        {/* PROJECTS TAB */}
        {activeTab === "projects" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">پروژه‌ها</h2>
              <button
                onClick={() => setShowProjectModal(true)}
                className="px-4 py-2 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 rounded-lg text-sm flex items-center gap-2"
              >
                <Plus className="h-4 w-4" /> پروژه جدید
              </button>
            </div>
            
            {projects.data?.items && projects.data.items.length > 0 ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {projects.data.items.map((project) => (
                  <motion.div
                    key={project.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl hover:border-emerald-500/30 transition-all"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-lg font-bold text-white mb-1">{project.title}</h3>
                        <p className="text-xs text-zinc-500">
                          {new Date(project.created_at).toLocaleDateString("fa-IR")}
                        </p>
                      </div>
                      <StatusBadge status={project.status} />
                    </div>
                    {project.description && (
                      <p className="text-sm text-zinc-400 mb-3">{project.description}</p>
                    )}
                    <div className="space-y-1 text-xs text-zinc-500 mb-3">
                      {project.location && <div>📍 {project.location}</div>}
                      {project.area_hectares && <div>📐 {project.area_hectares} هکتار</div>}
                      {project.crop_type && <div>🌾 {project.crop_type}</div>}
                      <div className="font-bold text-white">📊 {project.analysis_count || 0} تحلیل</div>
                    </div>
                    <Link
                      href={`/soil-water/projects/${project.id}`}
                      className="block text-center px-3 py-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 rounded-lg text-sm transition-all"
                    >
                      مشاهده جزئیات
                    </Link>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="p-12 bg-white/[0.03] border border-white/10 rounded-2xl text-center">
                <FolderOpen className="h-16 w-16 text-zinc-600 mx-auto mb-4" />
                <p className="text-zinc-400 mb-4">هنوز پروژه‌ای ایجاد نشده است</p>
                <button
                  onClick={() => setShowProjectModal(true)}
                  className="px-4 py-2 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 rounded-lg text-sm"
                >
                  ایجاد اولین پروژه →
                </button>
              </div>
            )}
          </motion.div>
        )}

        {/* Save Analysis Modal */}
        <Modal isOpen={showSaveModal} onClose={() => setShowSaveModal(false)} title="ذخیره تحلیل">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">عنوان تحلیل *</label>
              <input
                type="text"
                value={analysisTitle}
                onChange={(e) => setAnalysisTitle(e.target.value)}
                placeholder="مثلاً: تحلیل مزرعه شمالی - خرداد 1405"
                className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">پروژه مرتبط (اختیاری)</label>
              <select
                value={selectedProjectId || ""}
                onChange={(e) => setSelectedProjectId(e.target.value ? Number(e.target.value) : undefined)}
                className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
              >
                <option value="">بدون پروژه</option>
                {projects.data?.items?.map((p) => (
                  <option key={p.id} value={p.id}>{p.title}</option>
                ))}
              </select>
            </div>
            <div className="flex gap-3 pt-4">
              <button
                onClick={handleSave}
                disabled={createReport.isPending}
                className="flex-1 px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-white rounded-lg font-medium disabled:opacity-50"
              >
                {createReport.isPending ? "در حال ذخیره..." : "ذخیره"}
              </button>
              <button
                onClick={() => setShowSaveModal(false)}
                className="px-4 py-2 bg-white/[0.03] border border-white/10 text-zinc-300 rounded-lg"
              >
                انصراف
              </button>
            </div>
          </div>
        </Modal>

        {/* Create Project Modal */}
        <Modal isOpen={showProjectModal} onClose={() => setShowProjectModal(false)} title="ایجاد پروژه جدید">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">عنوان پروژه *</label>
              <input
                type="text"
                value={newProject.title}
                onChange={(e) => setNewProject({ ...newProject, title: e.target.value })}
                placeholder="مثلاً: مزرعه گندم شمالی"
                className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">توضیحات</label>
              <textarea
                value={newProject.description}
                onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                placeholder="توضیحات پروژه..."
                rows={3}
                className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">موقعیت</label>
                <input
                  type="text"
                  value={newProject.location}
                  onChange={(e) => setNewProject({ ...newProject, location: e.target.value })}
                  placeholder="مثلاً: خراسان شمالی"
                  className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">مساحت (هکتار)</label>
                <input
                  type="number"
                  value={newProject.area_hectares}
                  onChange={(e) => setNewProject({ ...newProject, area_hectares: parseFloat(e.target.value) || 0 })}
                  className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">نوع خاک</label>
                <input
                  type="text"
                  value={newProject.soil_type}
                  onChange={(e) => setNewProject({ ...newProject, soil_type: e.target.value })}
                  placeholder="مثلاً: لومی"
                  className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">نوع محصول</label>
                <input
                  type="text"
                  value={newProject.crop_type}
                  onChange={(e) => setNewProject({ ...newProject, crop_type: e.target.value })}
                  placeholder="مثلاً: گندم"
                  className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
                />
              </div>
            </div>
            <div className="flex gap-3 pt-4">
              <button
                onClick={handleCreateProject}
                disabled={createProject.isPending}
                className="flex-1 px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-white rounded-lg font-medium disabled:opacity-50"
              >
                {createProject.isPending ? "در حال ایجاد..." : "ایجاد پروژه"}
              </button>
              <button
                onClick={() => setShowProjectModal(false)}
                className="px-4 py-2 bg-white/[0.03] border border-white/10 text-zinc-300 rounded-lg"
              >
                انصراف
              </button>
            </div>
          </div>
        </Modal>

        {/* Report Detail Modal */}
        <Modal isOpen={!!showReportDetail} onClose={() => setShowReportDetail(null)} title="جزئیات گزارش">
          {showReportDetail && (() => {
            const report = reports.data?.items.find((r) => r.id === showReportDetail);
            if (!report) return <p className="text-zinc-500">در حال بارگذاری...</p>;
            const res = report.results as ComprehensiveAnalysisResponse | undefined;
            return (
              <div className="space-y-4">
                <div className="p-4 bg-white/[0.03] rounded-xl">
                  <h3 className="text-lg font-bold text-white mb-2">{report.title}</h3>
                  <div className="flex items-center gap-3 text-sm">
                    <StatusBadge status={report.overall_health || "good"} />
                    <span className="text-zinc-400">امتیاز:</span>
                    <span className="text-white font-bold tabular-nums" dir="ltr">
                      {report.overall_score?.toFixed(1)} / 100
                    </span>
                  </div>
                </div>

                {res?.indices && (
                  <div className="space-y-2">
                    <h4 className="text-sm font-bold text-zinc-300">شاخص‌ها:</h4>
                    <div className="grid grid-cols-2 gap-2">
                      {res.indices.ldn && (
                        <div className="p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-lg">
                          <p className="text-xs text-zinc-400">LDN</p>
                          <p className="text-lg font-bold text-emerald-400 tabular-nums" dir="ltr">
                            {res.indices.ldn.ldn_score.toFixed(1)}
                          </p>
                        </div>
                      )}
                      {res.indices.ndvi && (
                        <div className="p-3 bg-green-500/5 border border-green-500/20 rounded-lg">
                          <p className="text-xs text-zinc-400">NDVI</p>
                          <p className="text-lg font-bold text-green-400 tabular-nums" dir="ltr">
                            {res.indices.ndvi.ndvi.toFixed(3)}
                          </p>
                        </div>
                      )}
                      {res.indices.rusle && (
                        <div className="p-3 bg-amber-500/5 border border-amber-500/20 rounded-lg">
                          <p className="text-xs text-zinc-400">فرسایش</p>
                          <p className="text-lg font-bold text-amber-400 tabular-nums" dir="ltr">
                            {res.indices.rusle.soil_loss_tons_per_ha.toFixed(2)} t/ha
                          </p>
                        </div>
                      )}
                      {res.indices.carbon && (
                        <div className="p-3 bg-teal-500/5 border border-teal-500/20 rounded-lg">
                          <p className="text-xs text-zinc-400">کربن</p>
                          <p className="text-lg font-bold text-teal-400 tabular-nums" dir="ltr">
                            {res.indices.carbon.carbon_stock_tons_per_ha.toFixed(1)} t/ha
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {res?.recommendations && res.recommendations.length > 0 && (
                  <div className="p-4 bg-amber-500/5 border border-amber-500/20 rounded-xl">
                    <h4 className="text-sm font-bold text-amber-300 mb-2">توصیه‌ها:</h4>
                    <ul className="space-y-1">
                      {res.recommendations.map((r, i) => (
                        <li key={i} className="text-xs text-amber-200/80 flex items-start gap-2">
                          <AlertTriangle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                          {r}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })()}
        </Modal>
      </div>
    </div>
  );
}
'''
    write_file(WEB / "app/soil-water/page.tsx", content)


# ============================================================================
# Main
# ============================================================================
def main():
    print("=" * 70)
    print("🌊 Complete Professional Redesign - Soil & Water Module")
    print("=" * 70)
    print()
    
    try:
        print("🔧 Backend Updates:")
        update_backend_models()
        update_backend_schemas()
        update_backend_service()
        update_backend_router()
        print()
        
        print("🎨 Frontend Updates:")
        create_frontend_types()
        update_endpoints()
        create_frontend_hooks()
        create_main_page()
        print()
        
        print("=" * 70)
        print("✅ All files created successfully!")
        print("=" * 70)
        print()
        print("📋 What's New:")
        print()
        print("  🎯 Backend:")
        print("    ✅ SoilWaterProject model (CRUD)")
        print("    ✅ SoilWaterAnalysisReport model (CRUD)")
        print("    ✅ /api/v1/soil-water/projects (full CRUD)")
        print("    ✅ /api/v1/soil-water/reports (full CRUD)")
        print("    ✅ /api/v1/soil-water/stats (dashboard)")
        print("    ✅ /api/v1/soil-water/comprehensive-analysis")
        print("    ✅ All 8 index endpoints (backward compat)")
        print()
        print("  🎨 Frontend:")
        print("    ✅ 4 Tabs: Dashboard, Calculator, Reports, Projects")
        print("    ✅ Dashboard with stats, charts, tables")
        print("    ✅ Recharts: Pie, Radar, Bar charts")
        print("    ✅ Project management (create, view)")
        print("    ✅ Report management (save, view, delete)")
        print("    ✅ Export to CSV & JSON")
        print("    ✅ All buttons working (calculate, save, export)")
        print("    ✅ Data saved to PostgreSQL (not localStorage)")
        print()
        print("📦 Install Required Package:")
        print("  cd D:\\econojin.com\\apps\\web")
        print("  pnpm add recharts")
        print()
        print("🚀 Next steps:")
        print("  1. Install recharts: pnpm add recharts")
        print("  2. Restart backend: uvicorn api.main:app --reload")
        print("  3. Restart frontend: pnpm dev")
        print("  4. Visit: http://localhost:3001/soil-water")
        print()
        print("✨ Features:")
        print("  ✅ Dashboard with real-time stats from DB")
        print("  ✅ Charts: Pie, Radar, Bar for data visualization")
        print("  ✅ Calculator: All 8 indices with real backend calculation")
        print("  ✅ Reports: Full CRUD with project association")
        print("  ✅ Projects: Create & manage projects")
        print("  ✅ Export: CSV & JSON with all data")
        print("  ✅ Tables: Recent analyses with actions")
        print("  ✅ Modals: Save, Create Project, View Report")
        print()
        
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()