"""
Scientific Models Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.services.scientific_model_service import (
    get_all_models,
    get_model_by_id,
    update_model,
    increment_usage,
    seed_scientific_models,
)
from app.schemas.scientific_model import (
    ScientificModelResponse,
    ScientificModelUpdate,
    ScientificModelListResponse,
)
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=ScientificModelListResponse)
async def list_scientific_models(
    active_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    List all scientific models with metadata.
    Use active_only=True to get only active models.
    """
    result = await get_all_models(db, active_only=active_only)
    return ScientificModelListResponse(
        models=[ScientificModelResponse.model_validate(m) for m in result["models"]],
        total=result["total"],
        active_count=result["active_count"],
        featured_count=result["featured_count"],
        categories=result["categories"],
    )


@router.get("/{model_id}", response_model=ScientificModelResponse)
async def get_scientific_model(
    model_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific scientific model.
    """
    model = await get_model_by_id(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
    return ScientificModelResponse.model_validate(model)


@router.patch("/{model_id}", response_model=ScientificModelResponse)
async def update_scientific_model(
    model_id: str,
    update_data: ScientificModelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a scientific model's configuration (admin only).
    Can activate/deactivate models, update descriptions, etc.
    """
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    model = await update_model(db, model_id, update_data)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
    
    return ScientificModelResponse.model_validate(model)


@router.post("/{model_id}/usage")
async def record_model_usage(
    model_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Record usage of a scientific model (increments usage counter).
    """
    await increment_usage(db, model_id)
    return {"success": True, "message": f"Usage recorded for {model_id}"}


@router.post("/seed")
async def seed_models(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Seed all 40 scientific models into database (admin only).
    Only needs to be run once.
    """
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    await seed_scientific_models(db)
    return {"success": True, "message": "40 scientific models seeded successfully"}
