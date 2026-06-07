from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.core.deps import require_write_auth
from api.modules.farmer import crud, schemas

router = APIRouter(tags=["Farmers"])


@router.get("/", response_model=schemas.FarmerListResponse)
async def list_farmers(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    farmers, total = await crud.list_farmers(db, skip=skip, limit=limit)
    return schemas.FarmerListResponse(total=total, farmers=farmers)


@router.post("/", response_model=schemas.FarmerResponse, status_code=status.HTTP_201_CREATED)
async def create_farmer(
    farmer: schemas.FarmerCreate,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(require_write_auth),
):
    return await crud.create_farmer(db, farmer)


@router.get("/{farmer_id}", response_model=schemas.FarmerResponse)
async def get_farmer(farmer_id: int, db: AsyncSession = Depends(get_db)):
    farmer = await crud.get_farmer(db, farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found")
    return farmer


@router.put("/{farmer_id}", response_model=schemas.FarmerResponse)
async def update_farmer(
    farmer_id: int,
    farmer: schemas.FarmerUpdate,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(require_write_auth),
):
    updated = await crud.update_farmer(db, farmer_id, farmer)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found")
    return updated


@router.delete("/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=IDResponse)
async def delete_farmer(
    farmer_id: int,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(require_write_auth),
):
    if not await crud.delete_farmer(db, farmer_id):
        raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found")


@router.get("/{farmer_id}/activities", response_model=SuccessResponse)
async def get_farmer_activities(farmer_id: int, db: AsyncSession = Depends(get_db)):
    farmer = await crud.get_farmer(db, farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found")
    return {"farmer_id": farmer_id, "activities": []}
