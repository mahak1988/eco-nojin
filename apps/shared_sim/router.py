"""
shared_sim router | روتر shared_sim
=================================
FastAPI router exposing shared_sim endpoints.

Endpoints:
    GET    /shared_sim          List with pagination
    GET    /shared_sim/{id}    Get by ID
    POST   /shared_sim          Create
    PATCH  /shared_sim/{id}    Update
    DELETE /shared_sim/{id}    Delete
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

from apps.shared_sim.schemas import (
    SharedSimCreate,
    SharedSimUpdate,
    SharedSimResponse,
    SharedSimListResponse,
)
from apps.shared_sim.service import SharedSimService

router = APIRouter(prefix="/shared_sim", tags=["shared_sim"])


@router.get("", response_model=SharedSimListResponse)
async def list_shared_sim(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
):
    """List shared_sim records with pagination."""
    service = SharedSimService(session)
    items, total = await service.list(skip=skip, limit=limit)
    return SharedSimListResponse(
        items=[SharedSimResponse.model_validate(item) for item in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/{item_id}", response_model=SharedSimResponse)
async def get_shared_sim(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get a single shared_sim by ID."""
    service = SharedSimService(session)
    try:
        item = await service.get(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return SharedSimResponse.model_validate(item)


@router.post("", response_model=SharedSimResponse, status_code=status.HTTP_201_CREATED)
async def create_shared_sim(
    payload: SharedSimCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new shared_sim."""
    service = SharedSimService(session)
    item = await service.create(payload)
    await session.commit()
    return SharedSimResponse.model_validate(item)


@router.patch("/{item_id}", response_model=SharedSimResponse)
async def update_shared_sim(
    item_id: int,
    payload: SharedSimUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """Update an existing shared_sim."""
    service = SharedSimService(session)
    try:
        item = await service.update(item_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return SharedSimResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shared_sim(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Delete a shared_sim by ID."""
    service = SharedSimService(session)
    try:
        await service.delete(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return None
