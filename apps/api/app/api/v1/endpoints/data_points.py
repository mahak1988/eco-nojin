"""DataPoints Endpoints - Full CRUD"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.schemas.data_point import (
    DataPointCreate, DataPointUpdate, DataPointResponse, DataPointListResponse,
)
from app.services.data_point_service import (
    get_data_point_by_id, get_data_points, create_data_point,
    update_data_point, delete_data_point,
)


router = APIRouter()


@router.post("/", response_model=DataPointResponse, status_code=status.HTTP_201_CREATED)
async def create_data_point_endpoint(
    data_point_data: DataPointCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Submit a new data point"""
    data_point = await create_data_point(db, data_point_data, current_user.id)
    return data_point


@router.get("/", response_model=DataPointListResponse)
async def list_data_points(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    project_id: Optional[int] = None,
    module_id: Optional[int] = None,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """List data points with filters"""
    skip = (page - 1) * per_page
    data_points, total = await get_data_points(
        db, skip=skip, limit=per_page,
        project_id=project_id, module_id=module_id,
        user_id=user_id, status=status,
    )
    return DataPointListResponse(
        data_points=data_points,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{data_point_id}", response_model=DataPointResponse)
async def get_data_point(
    data_point_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Get data point by ID"""
    data_point = await get_data_point_by_id(db, data_point_id)
    if not data_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data point not found",
        )
    return data_point


@router.patch("/{data_point_id}", response_model=DataPointResponse)
async def update_data_point_endpoint(
    data_point_id: int,
    data_point_data: DataPointUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Update data point (creator or admin)"""
    data_point = await get_data_point_by_id(db, data_point_id)
    if not data_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data point not found",
        )
    
    if current_user.role.value != "admin" and data_point.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this data point",
        )
    
    return await update_data_point(db, data_point, data_point_data)


@router.delete("/{data_point_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data_point_endpoint(
    data_point_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(["admin"])),
):
    """Delete data point (admin only)"""
    data_point = await get_data_point_by_id(db, data_point_id)
    if not data_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data point not found",
        )
    
    await delete_data_point(db, data_point)
