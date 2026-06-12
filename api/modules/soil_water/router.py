"""
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
