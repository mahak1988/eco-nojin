# api/modules/water/router.py

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.modules.water import models as water_models
from api.modules.water.schemas import SimulationRequest, WaterBalanceRead
from api.modules.water.service import WaterSimulationService

router = APIRouter(prefix="/water", tags=["water"])


# ---------- Queries ----------


@router.get(
    "/balance",
    response_model=List[WaterBalanceRead],
)
def get_water_balance(
    scenario_id: int = Query(..., description="Scenario ID for filtering results"),
    start_date: Optional[date] = Query(
        None, description="Optional start date for filtering results"
    ),
    end_date: Optional[date] = Query(
        None, description="Optional end date for filtering results"
    ),
    db: Session = Depends(get_db),
):
    """
    Read water balance time series stored in DB for a given scenario.
    """

    query = db.query(water_models.WaterBalance).filter(
        water_models.WaterBalance.scenario_id == scenario_id
    )
    if start_date is not None:
        query = query.filter(water_models.WaterBalance.date >= start_date)
    if end_date is not None:
        query = query.filter(water_models.WaterBalance.date <= end_date)

    rows = query.order_by(water_models.WaterBalance.date).all()
    return rows


# ---------- Commands ----------


@router.post(
    "/simulate",
    response_model=List[WaterBalanceRead],
    status_code=201,
)
def simulate_water_balance(
    payload: SimulationRequest,
    db: Session = Depends(get_db),
):
    """
    Run soil–water simulation through the scientific core and persist results.

    This endpoint is **idempotent per scenario**:
    - Deletes previous WaterBalance entries for the given scenario_id
    - Writes fresh outputs for the provided input series
    """

    service = WaterSimulationService(db=db)

    try:
        entities = service.run_simulation(
            scenario_id=payload.scenario_id,
            soil_profile_id=payload.soil_profile_id,
            daily_inputs=payload.daily_inputs,
        )
    except ValueError as exc:
        # domain-level errors mapped to HTTP
        msg = str(exc)
        if "soil_profile_not_found" in msg:
            raise HTTPException(
                status_code=404, detail="Soil profile not found"
            ) from exc
        raise HTTPException(status_code=400, detail=msg) from exc
    except RuntimeError as exc:
        # unexpected output from core
        raise HTTPException(
            status_code=500,
            detail=f"SoilWaterCoreService error: {exc}",
        ) from exc

    return entities