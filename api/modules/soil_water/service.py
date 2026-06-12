"""
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


"""
Soil & Water Service - Scientific Calculations
"""
from typing import Optional, Tuple, List
from datetime import datetime, date, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.soil_water.models import (
    SoilWaterAnalysis, WaterBalance, Scenario, IrrigationSchedule,
    DroughtIndex, VegetationIndex, SoilErosionRisk, CarbonSequestration
)
from api.modules.soil_water import schemas


# ============================================================================
# Soil Water Analysis Functions
# ============================================================================
async def list_analyses(
    db: AsyncSession,
    farmer_id: Optional[int] = None,
    limit: int = 10,
    offset: int = 0,
) -> Tuple[int, List[dict]]:
    """List soil water analyses"""
    query = select(SoilWaterAnalysis)
    
    if farmer_id:
        query = query.where(SoilWaterAnalysis.farmer_id == farmer_id)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    query = query.order_by(SoilWaterAnalysis.created_at.desc())
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    items_dict = []
    for item in items:
        items_dict.append({
            "id": item.id,
            "farmer_id": item.farmer_id,
            "location_id": item.location_id,
            "field_name": item.field_name,
            "soil_texture": item.soil_texture,
            "bulk_density": item.bulk_density,
            "field_capacity": item.field_capacity,
            "wilting_point": item.wilting_point,
            "saturation_percentage": item.saturation_percentage,
            "available_water_capacity": item.available_water_capacity,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        })
    
    return total, items_dict


async def create_analysis(
    db: AsyncSession,
    payload: schemas.SoilWaterAnalysisCreate,
) -> dict:
    """Create a new soil water analysis"""
    analysis = SoilWaterAnalysis(
        farmer_id=payload.farmer_id,
        location_id=payload.location_id,
        field_name=payload.field_name,
        soil_texture=payload.soil_texture,
        bulk_density=payload.bulk_density,
        field_capacity=payload.field_capacity,
        wilting_point=payload.wilting_point,
        saturation_percentage=payload.saturation_percentage,
        available_water_capacity=payload.available_water_capacity,
    )
    
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    
    return {
        "id": analysis.id,
        "farmer_id": analysis.farmer_id,
        "field_name": analysis.field_name,
        "soil_texture": analysis.soil_texture,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
    }


async def get_analysis(db: AsyncSession, analysis_id: int) -> Optional[dict]:
    """Get a specific analysis"""
    result = await db.execute(
        select(SoilWaterAnalysis).where(SoilWaterAnalysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        return None
    
    return {
        "id": analysis.id,
        "farmer_id": analysis.farmer_id,
        "field_name": analysis.field_name,
        "soil_texture": analysis.soil_texture,
        "bulk_density": analysis.bulk_density,
        "field_capacity": analysis.field_capacity,
        "wilting_point": analysis.wilting_point,
    }


# ============================================================================
# Scientific Calculations
# ============================================================================
def calculate_ldn(soil_organic_carbon: float, vegetation_cover: float, erosion_risk: float) -> dict:
    """
    Calculate Land Degradation Neutrality (LDN) index
    
    LDN = (SOC * 0.4) + (VC * 0.35) + ((100 - ER) * 0.25)
    
    Where:
    - SOC: Soil Organic Carbon (%)
    - VC: Vegetation Cover (%)
    - ER: Erosion Risk (%)
    """
    ldn_score = (
        (soil_organic_carbon * 0.4) +
        (vegetation_cover * 0.35) +
        ((100 - erosion_risk) * 0.25)
    )
    
    if ldn_score > 70:
        status = "healthy"
    elif ldn_score > 40:
        status = "degraded"
    else:
        status = "critical"
    
    return {
        "ldn_score": round(ldn_score, 2),
        "status": status,
        "soil_organic_carbon": soil_organic_carbon,
        "vegetation_cover": vegetation_cover,
        "erosion_risk": erosion_risk,
    }


def calculate_water_balance(
    precipitation: float,
    evapotranspiration: float,
    runoff_coefficient: float = 0.3,
    soil_moisture_initial: float = 50.0,
) -> dict:
    """
    Calculate water balance
    
    WB = P - ET - R - ΔS
    
    Where:
    - P: Precipitation (mm)
    - ET: Evapotranspiration (mm)
    - R: Runoff (mm)
    - ΔS: Change in soil moisture (mm)
    """
    runoff = precipitation * runoff_coefficient
    net_water = precipitation - evapotranspiration - runoff
    soil_moisture_final = max(0, soil_moisture_initial + net_water)
    soil_moisture_change = soil_moisture_final - soil_moisture_initial
    
    return {
        "precipitation": precipitation,
        "evapotranspiration": evapotranspiration,
        "runoff": round(runoff, 2),
        "net_water": round(net_water, 2),
        "soil_moisture_initial": soil_moisture_initial,
        "soil_moisture_final": round(soil_moisture_final, 2),
        "soil_moisture_change": round(soil_moisture_change, 2),
        "water_surplus": net_water > 0,
    }


def calculate_ndvi(nir: float, red: float) -> float:
    """
    Calculate Normalized Difference Vegetation Index (NDVI)
    
    NDVI = (NIR - Red) / (NIR + Red)
    
    Range: -1 to 1
    - Negative: Water, clouds, snow
    - 0 to 0.2: Bare soil
    - 0.2 to 0.4: Sparse vegetation
    - 0.4 to 0.6: Moderate vegetation
    - 0.6 to 1.0: Dense vegetation
    """
    if (nir + red) == 0:
        return 0.0
    
    ndvi = (nir - red) / (nir + red)
    return round(ndvi, 4)


def calculate_ndwi(green: float, nir: float) -> float:
    """
    Calculate Normalized Difference Water Index (NDWI)
    
    NDWI = (Green - NIR) / (Green + NIR)
    
    Range: -1 to 1
    - Positive: Water bodies
    - Negative: Vegetation, soil
    """
    if (green + nir) == 0:
        return 0.0
    
    ndwi = (green - nir) / (green + nir)
    return round(ndwi, 4)


def calculate_rusle(
    r_factor: float,
    k_factor: float,
    ls_factor: float,
    c_factor: float,
    p_factor: float,
) -> dict:
    """
    Calculate Revised Universal Soil Loss Equation (RUSLE)
    
    A = R * K * LS * C * P
    
    Where:
    - A: Soil loss (tons/ha/year)
    - R: Rainfall erosivity factor
    - K: Soil erodibility factor
    - LS: Slope length & steepness factor
    - C: Cover management factor
    - P: Support practices factor
    """
    soil_loss = r_factor * k_factor * ls_factor * c_factor * p_factor
    
    if soil_loss < 5:
        category = "low"
    elif soil_loss < 15:
        category = "moderate"
    elif soil_loss < 30:
        category = "high"
    else:
        category = "very_high"
    
    return {
        "soil_loss_tons_per_ha": round(soil_loss, 2),
        "erosion_risk_category": category,
        "r_factor": r_factor,
        "k_factor": k_factor,
        "ls_factor": ls_factor,
        "c_factor": c_factor,
        "p_factor": p_factor,
    }


def calculate_irrigation_requirement(
    crop_type: str,
    field_capacity: float,
    wilting_point: float,
    current_moisture: float,
    et_crop: float,
    efficiency: float = 0.7,
) -> dict:
    """
    Calculate irrigation water requirement
    
    IR = (FC - WP) * (1 - (θ/FC)) * Z / Ea
    
    Where:
    - FC: Field capacity (%)
    - WP: Wilting point (%)
    - θ: Current soil moisture (%)
    - Z: Root zone depth (mm)
    - Ea: Application efficiency
    """
    available_water = field_capacity - wilting_point
    depletion = field_capacity - current_moisture
    depletion_fraction = depletion / available_water if available_water > 0 else 0
    
    root_zone_depth = 500  # mm (default)
    water_requirement = (depletion * root_zone_depth) / efficiency
    
    irrigation_interval = water_requirement / et_crop if et_crop > 0 else 7
    
    return {
        "water_requirement_mm": round(water_requirement, 2),
        "irrigation_interval_days": max(1, int(irrigation_interval)),
        "efficiency_percentage": efficiency * 100,
        "depletion_fraction": round(depletion_fraction, 2),
        "crop_type": crop_type,
        "recommended_date": (date.today() + timedelta(days=1)).isoformat(),
    }


def classify_drought(spi: float) -> str:
    """
    Classify drought based on Standardized Precipitation Index (SPI)
    
    SPI Categories:
    - ≥ 2.0: Extremely wet
    - 1.5 to 1.99: Very wet
    - 1.0 to 1.49: Moderately wet
    - -0.99 to 0.99: Near normal
    - -1.0 to -1.49: Moderately dry
    - -1.5 to -1.99: Severely dry
    - ≤ -2.0: Extremely dry
    """
    if spi >= 2.0:
        return "extremely_wet"
    elif spi >= 1.5:
        return "very_wet"
    elif spi >= 1.0:
        return "moderately_wet"
    elif spi >= -0.99:
        return "near_normal"
    elif spi >= -1.49:
        return "moderately_dry"
    elif spi >= -1.99:
        return "severely_dry"
    else:
        return "extremely_dry"


def calculate_carbon_sequestration(
    soil_organic_carbon_pct: float,
    bulk_density: float,
    depth_cm: float = 30,
) -> dict:
    """
    Calculate carbon stock in soil
    
    Carbon Stock (tons/ha) = SOC% * BD * Depth * 10
    
    Where:
    - SOC: Soil organic carbon (%)
    - BD: Bulk density (g/cm³)
    - Depth: Soil depth (cm)
    """
    carbon_stock = soil_organic_carbon_pct * bulk_density * depth_cm * 10
    
    return {
        "carbon_stock_tons_per_ha": round(carbon_stock, 2),
        "soil_organic_carbon_pct": soil_organic_carbon_pct,
        "bulk_density": bulk_density,
        "depth_cm": depth_cm,
    }


# ============================================================================
# COMPREHENSIVE ANALYSIS - All indices in one call
# ============================================================================
def comprehensive_analysis(data: dict) -> dict:
    """
    Perform comprehensive soil & water analysis
    Calculates all 8 indices and returns aggregated results
    """
    result = {
        "indices": {},
        "overall_health": "good",
        "overall_score": 0,
        "recommendations": [],
        "timestamp": None,
    }
    
    scores = []
    
    # 1. LDN Calculation
    if "ldn" in data and data["ldn"]:
        ldn = data["ldn"]
        soc = float(ldn.get("soil_organic_carbon", 0))
        vc = float(ldn.get("vegetation_cover", 0))
        er = float(ldn.get("erosion_risk", 0))
        
        ldn_score = (soc * 0.4) + (vc * 0.35) + ((100 - er) * 0.25)
        ldn_score = max(0, min(100, ldn_score))
        
        if ldn_score > 70:
            status = "healthy"
        elif ldn_score > 40:
            status = "degraded"
        else:
            status = "critical"
        
        result["indices"]["ldn"] = {
            "ldn_score": round(ldn_score, 2),
            "status": status,
            "soil_organic_carbon": soc,
            "vegetation_cover": vc,
            "erosion_risk": er,
        }
        scores.append(ldn_score)
        
        if status == "critical":
            result["recommendations"].append("اقدام فوری برای جلوگیری از تخریب زمین لازم است")
        elif status == "degraded":
            result["recommendations"].append("افزایش پوشش گیاهی و بهبود مدیریت خاک توصیه می‌شود")
    
    # 2. NDVI Calculation
    if "ndvi" in data and data["ndvi"]:
        nd = data["ndvi"]
        nir = float(nd.get("nir", 0))
        red = float(nd.get("red", 0))
        
        if (nir + red) == 0:
            ndvi_val = 0.0
        else:
            ndvi_val = (nir - red) / (nir + red)
        ndvi_val = max(-1, min(1, ndvi_val))
        
        if ndvi_val < 0:
            health = "non_vegetation"
        elif ndvi_val < 0.2:
            health = "bare_soil"
        elif ndvi_val < 0.4:
            health = "sparse_vegetation"
        elif ndvi_val < 0.6:
            health = "moderate_vegetation"
        else:
            health = "dense_vegetation"
        
        result["indices"]["ndvi"] = {
            "ndvi": round(ndvi_val, 4),
            "vegetation_health": health,
        }
        scores.append(ndvi_val * 100)
        
        if ndvi_val < 0.2:
            result["recommendations"].append("پوشش گیاهی بسیار ضعیف - کشت مجدد یا آبیاری ضروری است")
    
    # 3. NDWI Calculation
    if "ndwi" in data and data["ndwi"]:
        nw = data["ndwi"]
        green = float(nw.get("green", 0))
        nir = float(nw.get("nir", 0))
        
        if (green + nir) == 0:
            ndwi_val = 0.0
        else:
            ndwi_val = (green - nir) / (green + nir)
        ndwi_val = max(-1, min(1, ndwi_val))
        
        result["indices"]["ndwi"] = {
            "ndwi": round(ndwi_val, 4),
            "water_presence": ndwi_val > 0,
        }
    
    # 4. RUSLE Calculation
    if "rusle" in data and data["rusle"]:
        r = data["rusle"]
        rf = float(r.get("r_factor", 0))
        kf = float(r.get("k_factor", 0))
        lsf = float(r.get("ls_factor", 0))
        cf = float(r.get("c_factor", 0))
        pf = float(r.get("p_factor", 0))
        
        soil_loss = rf * kf * lsf * cf * pf
        
        if soil_loss < 5:
            cat = "low"
        elif soil_loss < 15:
            cat = "moderate"
        elif soil_loss < 30:
            cat = "high"
        else:
            cat = "very_high"
        
        result["indices"]["rusle"] = {
            "soil_loss_tons_per_ha": round(soil_loss, 2),
            "erosion_risk_category": cat,
            "r_factor": rf, "k_factor": kf, "ls_factor": lsf,
            "c_factor": cf, "p_factor": pf,
        }
        
        rusle_score = max(0, 100 - soil_loss * 2)
        scores.append(rusle_score)
        
        if cat == "very_high":
            result["recommendations"].append("فرسایش خاک بحرانی - عملیات حفاظتی فوری (تراس، پوشش گیاهی) ضروری است")
        elif cat == "high":
            result["recommendations"].append("خطر فرسایش بالا - ایجاد تراس و پوشش گیاهی توصیه می‌شود")
    
    # 5. Water Balance
    if "water_balance" in data and data["water_balance"]:
        wb = data["water_balance"]
        p = float(wb.get("precipitation", 0))
        et = float(wb.get("evapotranspiration", 0))
        rc = float(wb.get("runoff_coefficient", 0.3))
        smi = float(wb.get("soil_moisture_initial", 50))
        
        runoff = p * rc
        net_water = p - et - runoff
        smf = max(0, smi + net_water)
        smc = smf - smi
        
        result["indices"]["water_balance"] = {
            "precipitation": p,
            "evapotranspiration": et,
            "runoff": round(runoff, 2),
            "net_water": round(net_water, 2),
            "soil_moisture_initial": smi,
            "soil_moisture_final": round(smf, 2),
            "soil_moisture_change": round(smc, 2),
            "water_surplus": net_water > 0,
        }
        
        if net_water < 0:
            result["recommendations"].append("کسری بیلان آبی - نیاز به آبیاری تکمیلی یا مدیریت مصرف")
    
    # 6. Irrigation
    if "irrigation" in data and data["irrigation"]:
        ir = data["irrigation"]
        fc = float(ir.get("field_capacity", 0))
        wp = float(ir.get("wilting_point", 0))
        cm = float(ir.get("current_moisture", 0))
        etc = float(ir.get("et_crop", 0))
        eff = float(ir.get("efficiency", 0.7))
        crop = ir.get("crop_type", "generic")
        
        aw = fc - wp
        depletion = fc - cm
        z = 500  # root zone depth mm
        
        if eff > 0:
            wr = (depletion * z) / eff
        else:
            wr = 0
        
        interval = max(1, int(wr / etc)) if etc > 0 else 7
        
        from datetime import date, timedelta
        rec_date = (date.today() + timedelta(days=1)).isoformat()
        
        result["indices"]["irrigation"] = {
            "water_requirement_mm": round(wr, 2),
            "irrigation_interval_days": interval,
            "efficiency_percentage": round(eff * 100, 1),
            "depletion_fraction": round(depletion / aw, 2) if aw > 0 else 0,
            "crop_type": crop,
            "recommended_date": rec_date,
        }
    
    # 7. Drought (SPI)
    if "drought" in data and data["drought"]:
        dr = data["drought"]
        spi = float(dr.get("spi", 0))
        
        if spi >= 2.0:
            cat = "extremely_wet"
        elif spi >= 1.5:
            cat = "very_wet"
        elif spi >= 1.0:
            cat = "moderately_wet"
        elif spi >= -0.99:
            cat = "near_normal"
        elif spi >= -1.49:
            cat = "moderately_dry"
        elif spi >= -1.99:
            cat = "severely_dry"
        else:
            cat = "extremely_dry"
        
        result["indices"]["drought"] = {
            "spi": round(spi, 2),
            "drought_category": cat,
        }
        
        drought_score = ((spi + 3) / 6) * 100
        scores.append(max(0, min(100, drought_score)))
        
        if spi < -1.5:
            result["recommendations"].append("خشکسالی شدید - مدیریت اضطراری منابع آبی و کاهش مصرف ضروری است")
        elif spi < -1.0:
            result["recommendations"].append("شرایط خشک - پایش منظم و آماده‌باش برای آبیاری تکمیلی")
    
    # 8. Carbon Sequestration
    if "carbon" in data and data["carbon"]:
        c = data["carbon"]
        soc = float(c.get("soil_organic_carbon_pct", 0))
        bd = float(c.get("bulk_density", 0))
        depth = float(c.get("depth_cm", 30))
        
        carbon_stock = soc * bd * depth * 10
        
        result["indices"]["carbon"] = {
            "carbon_stock_tons_per_ha": round(carbon_stock, 2),
            "soil_organic_carbon_pct": soc,
            "bulk_density": bd,
            "depth_cm": depth,
        }
    
    # Overall Score & Health
    if scores:
        avg = sum(scores) / len(scores)
        result["overall_score"] = round(avg, 2)
        
        if avg >= 75:
            result["overall_health"] = "excellent"
        elif avg >= 50:
            result["overall_health"] = "good"
        elif avg >= 30:
            result["overall_health"] = "warning"
        else:
            result["overall_health"] = "critical"
    
    from datetime import datetime
    result["timestamp"] = datetime.utcnow().isoformat()
    
    if not result["recommendations"]:
        result["recommendations"].append("وضعیت زمین مطلوب است - ادامه مدیریت فعلی توصیه می‌شود")
    
    return result


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


