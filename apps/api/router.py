"""
api router | روتر api
=================================
FastAPI router exposing api endpoints.

Endpoints:
    GET    /api          List with pagination
    GET    /api/{id}    Get by ID
    POST   /api          Create
    PATCH  /api/{id}    Update
    DELETE /api/{id}    Delete
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Adjust this import to match your project's database session dependency
try:
    from apps.shared_core.database.session import get_db_session
except ImportError:
    # Fallback stub — replace with real implementation
    from typing import AsyncGenerator
    async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
        raise NotImplementedError("Wire up get_db_session in apps.shared_core.database.session")

from apps.api.schemas import (
    ApiCreate,
    ApiUpdate,
    ApiResponse,
    ApiListResponse,
)
from apps.api.service import ApiService

router = APIRouter(prefix="/api", tags=["api"])


@router.get("", response_model=ApiListResponse)
async def list_api(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
):
    """List api records with pagination."""
    service = ApiService(session)
    items, total = await service.list(skip=skip, limit=limit)
    return ApiListResponse(
        items=[ApiResponse.model_validate(item) for item in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/{item_id}", response_model=ApiResponse)
async def get_api(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get a single api by ID."""
    service = ApiService(session)
    try:
        item = await service.get(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return ApiResponse.model_validate(item)


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_api(
    payload: ApiCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new api."""
    service = ApiService(session)
    item = await service.create(payload)
    await session.commit()
    return ApiResponse.model_validate(item)


@router.patch("/{item_id}", response_model=ApiResponse)
async def update_api(
    item_id: int,
    payload: ApiUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """Update an existing api."""
    service = ApiService(session)
    try:
        item = await service.update(item_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return ApiResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Delete a api by ID."""
    service = ApiService(session)
    try:
        await service.delete(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return None
