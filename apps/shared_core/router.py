"""
shared_core router | روتر shared_core
=================================
FastAPI router exposing shared_core endpoints.

Endpoints:
    GET    /shared_core          List with pagination
    GET    /shared_core/{id}    Get by ID
    POST   /shared_core          Create
    PATCH  /shared_core/{id}    Update
    DELETE /shared_core/{id}    Delete
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

from apps.shared_core.schemas import (
    SharedCoreCreate,
    SharedCoreUpdate,
    SharedCoreResponse,
    SharedCoreListResponse,
)
from apps.shared_core.service import SharedCoreService

router = APIRouter(prefix="/shared_core", tags=["shared_core"])


@router.get("", response_model=SharedCoreListResponse)
async def list_shared_core(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
):
    """List shared_core records with pagination."""
    service = SharedCoreService(session)
    items, total = await service.list(skip=skip, limit=limit)
    return SharedCoreListResponse(
        items=[SharedCoreResponse.model_validate(item) for item in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/{item_id}", response_model=SharedCoreResponse)
async def get_shared_core(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get a single shared_core by ID."""
    service = SharedCoreService(session)
    try:
        item = await service.get(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return SharedCoreResponse.model_validate(item)


@router.post("", response_model=SharedCoreResponse, status_code=status.HTTP_201_CREATED)
async def create_shared_core(
    payload: SharedCoreCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new shared_core."""
    service = SharedCoreService(session)
    item = await service.create(payload)
    await session.commit()
    return SharedCoreResponse.model_validate(item)


@router.patch("/{item_id}", response_model=SharedCoreResponse)
async def update_shared_core(
    item_id: int,
    payload: SharedCoreUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """Update an existing shared_core."""
    service = SharedCoreService(session)
    try:
        item = await service.update(item_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return SharedCoreResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shared_core(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Delete a shared_core by ID."""
    service = SharedCoreService(session)
    try:
        await service.delete(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return None
