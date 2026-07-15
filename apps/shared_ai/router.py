"""
shared_ai router | روتر shared_ai
=================================
FastAPI router exposing shared_ai endpoints.

Endpoints:
    GET    /shared_ai          List with pagination
    GET    /shared_ai/{id}    Get by ID
    POST   /shared_ai          Create
    PATCH  /shared_ai/{id}    Update
    DELETE /shared_ai/{id}    Delete
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

from apps.shared_ai.schemas import (
    SharedAiCreate,
    SharedAiUpdate,
    SharedAiResponse,
    SharedAiListResponse,
)
from apps.shared_ai.service import SharedAiService

router = APIRouter(prefix="/shared_ai", tags=["shared_ai"])


@router.get("", response_model=SharedAiListResponse)
async def list_shared_ai(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
):
    """List shared_ai records with pagination."""
    service = SharedAiService(session)
    items, total = await service.list(skip=skip, limit=limit)
    return SharedAiListResponse(
        items=[SharedAiResponse.model_validate(item) for item in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/{item_id}", response_model=SharedAiResponse)
async def get_shared_ai(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get a single shared_ai by ID."""
    service = SharedAiService(session)
    try:
        item = await service.get(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return SharedAiResponse.model_validate(item)


@router.post("", response_model=SharedAiResponse, status_code=status.HTTP_201_CREATED)
async def create_shared_ai(
    payload: SharedAiCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new shared_ai."""
    service = SharedAiService(session)
    item = await service.create(payload)
    await session.commit()
    return SharedAiResponse.model_validate(item)


@router.patch("/{item_id}", response_model=SharedAiResponse)
async def update_shared_ai(
    item_id: int,
    payload: SharedAiUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """Update an existing shared_ai."""
    service = SharedAiService(session)
    try:
        item = await service.update(item_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return SharedAiResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shared_ai(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Delete a shared_ai by ID."""
    service = SharedAiService(session)
    try:
        await service.delete(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return None
