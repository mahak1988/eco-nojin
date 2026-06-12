from pathlib import Path

# ============================================================================
# 1. Create schemas.py
# ============================================================================
schemas_content = '''"""
Soil & Water Schemas
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class SoilWaterAnalysisBase(BaseModel):
    farmer_id: int
    location_id: Optional[int] = None
    field_name: Optional[str] = None
    soil_texture: Optional[str] = None
    bulk_density: Optional[float] = None
    field_capacity: Optional[float] = None
    wilting_point: Optional[float] = None


class SoilWaterAnalysisCreate(SoilWaterAnalysisBase):
    pass


class SoilWaterAnalysisResponse(SoilWaterAnalysisBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SoilWaterAnalysisList(BaseModel):
    total: int
    items: List[SoilWaterAnalysisResponse]
'''

schemas_path = Path("api/modules/soil_water/schemas.py")
schemas_path.write_text(schemas_content, encoding='utf-8')
print(f"✅ Created: {schemas_path}")


# ============================================================================
# 2. Create service.py (async version)
# ============================================================================
service_content = '''"""
Soil & Water Service (Async)
"""
from typing import Optional, Tuple, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.soil_water.models import SoilWaterAnalysis
from api.modules.soil_water import schemas


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
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get items
    query = query.order_by(SoilWaterAnalysis.created_at.desc())
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Convert to dict
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
    )
    
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    
    return {
        "id": analysis.id,
        "farmer_id": analysis.farmer_id,
        "location_id": analysis.location_id,
        "field_name": analysis.field_name,
        "soil_texture": analysis.soil_texture,
        "bulk_density": analysis.bulk_density,
        "field_capacity": analysis.field_capacity,
        "wilting_point": analysis.wilting_point,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
    }


async def get_analysis(
    db: AsyncSession,
    analysis_id: int,
) -> Optional[dict]:
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
        "location_id": analysis.location_id,
        "field_name": analysis.field_name,
        "soil_texture": analysis.soil_texture,
        "bulk_density": analysis.bulk_density,
        "field_capacity": analysis.field_capacity,
        "wilting_point": analysis.wilting_point,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
        "updated_at": analysis.updated_at.isoformat() if analysis.updated_at else None,
    }
'''

service_path = Path("api/modules/soil_water/service.py")
service_path.write_text(service_content, encoding='utf-8')
print(f"✅ Created: {service_path}")


# ============================================================================
# 3. Verify router.py
# ============================================================================
router_path = Path("api/modules/soil_water/router.py")
if router_path.exists():
    content = router_path.read_text(encoding='utf-8')
    print(f"✅ Router exists ({len(content)} bytes)")
else:
    print("❌ Router not found!")


# ============================================================================
# 4. Delete database
# ============================================================================
for db in [Path("econojin.db"), Path("api/econojin.db")]:
    if db.exists():
        try:
            db.unlink()
            print(f"🗑️ Deleted: {db}")
        except Exception as e:
            print(f"⚠️ Cannot delete {db}: {e}")


print("\n" + "=" * 70)
print("✅ All files created!")
print("=" * 70)
print("\nNext steps:")
print("1. Stop backend server (Ctrl+C)")
print("2. Remove-Item 'econojin.db' -Force")
print("3. uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")