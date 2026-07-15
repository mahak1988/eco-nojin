"""
shared router | روتر shared
=================================
FastAPI router exposing shared endpoints.

Endpoints:
    GET    /shared          List with pagination
    GET    /shared/{id}    Get by ID
    POST   /shared          Create
    PATCH  /shared/{id}    Update
    DELETE /shared/{id}    Delete
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

from apps.shared.schemas import (
    SharedCreate,
    SharedUpdate,
    SharedResponse,
    SharedListResponse,
)
from apps.shared.service import SharedService

router = APIRouter(prefix="/shared", tags=["shared"])


@router.get("", response_model=SharedListResponse)
async def list_shared(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
):
    """List shared records with pagination."""
    service = SharedService(session)
    items, total = await service.list(skip=skip, limit=limit)
    return SharedListResponse(
        items=[SharedResponse.model_validate(item) for item in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/{item_id}", response_model=SharedResponse)
async def get_shared(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get a single shared by ID."""
    service = SharedService(session)
    try:
        item = await service.get(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return SharedResponse.model_validate(item)


@router.post("", response_model=SharedResponse, status_code=status.HTTP_201_CREATED)
async def create_shared(
    payload: SharedCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new shared."""
    service = SharedService(session)
    item = await service.create(payload)
    await session.commit()
    return SharedResponse.model_validate(item)


@router.patch("/{item_id}", response_model=SharedResponse)
async def update_shared(
    item_id: int,
    payload: SharedUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """Update an existing shared."""
    service = SharedService(session)
    try:
        item = await service.update(item_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return SharedResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shared(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Delete a shared by ID."""
    service = SharedService(session)
    try:
        await service.delete(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return None
