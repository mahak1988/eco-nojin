from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from api.modules.soil_water import erosion_models, erosion_schemas
from api.services.soil_water.erosion_services import (
    RUSLEFactors,
    compute_rusle,
)


def create_erosion_analysis(
    db: Session,
    data: erosion_schemas.SoilErosionCreate,
) -> erosion_models.SoilErosionAnalysis:
    factors = RUSLEFactors(
        R=data.R,
        K=data.K,
        LS=data.LS,
        C=data.C,
        P=data.P,
    )
    result = compute_rusle(factors)

    obj = erosion_models.SoilErosionAnalysis(
        farmer_id=data.farmer_id,
        location_id=data.location_id,
        R=data.R,
        K=data.K,
        LS=data.LS,
        C=data.C,
        P=data.P,
        annual_soil_loss=result["annual_soil_loss"],
        risk_class=result["risk_class"],
        title=data.title,
        description=data.description,
        meta={"source": "RUSLE_v1"},
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_erosion_analysis(
    db: Session,
    analysis_id: int,
) -> Optional[erosion_models.SoilErosionAnalysis]:
    return db.get(erosion_models.SoilErosionAnalysis, analysis_id)


def list_erosion_analyses(
    db: Session,
    farmer_id: Optional[int] = None,
    location_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[int, List[erosion_models.SoilErosionAnalysis]]:
    query = select(erosion_models.SoilErosionAnalysis)

    if farmer_id is not None:
        query = query.where(erosion_models.SoilErosionAnalysis.farmer_id == farmer_id)
    if location_id is not None:
        query = query.where(erosion_models.SoilErosionAnalysis.location_id == location_id)

    total = db.execute(
        select(func.count()).select_from(query.subquery())
    ).scalar_one()

    items = (
        db.execute(
            query.order_by(erosion_models.SoilErosionAnalysis.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        .scalars()
        .all()
    )

    return total, items


def update_erosion_analysis(
    db: Session,
    analysis_id: int,
    data: erosion_schemas.SoilErosionUpdate,
) -> Optional[erosion_models.SoilErosionAnalysis]:
    obj = get_erosion_analysis(db, analysis_id)
    if not obj:
        return None

    if data.title is not None:
        obj.title = data.title
    if data.description is not None:
        obj.description = data.description
    if data.location_id is not None:
        obj.location_id = data.location_id

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj