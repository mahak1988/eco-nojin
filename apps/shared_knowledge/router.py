"""
shared_knowledge router | روتر shared_knowledge
=================================
FastAPI router exposing shared_knowledge endpoints.

Endpoints:
    GET    /shared_knowledge          List with pagination
    GET    /shared_knowledge/{id}    Get by ID
    POST   /shared_knowledge          Create
    PATCH  /shared_knowledge/{id}    Update
    DELETE /shared_knowledge/{id}    Delete
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

from apps.shared_knowledge.schemas import (
    SharedKnowledgeCreate,
    SharedKnowledgeUpdate,
    SharedKnowledgeResponse,
    SharedKnowledgeListResponse,
)
from apps.shared_knowledge.service import SharedKnowledgeService

router = APIRouter(prefix="/shared_knowledge", tags=["shared_knowledge"])


@router.get("", response_model=SharedKnowledgeListResponse)
async def list_shared_knowledge(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
):
    """List shared_knowledge records with pagination."""
    service = SharedKnowledgeService(session)
    items, total = await service.list(skip=skip, limit=limit)
    return SharedKnowledgeListResponse(
        items=[SharedKnowledgeResponse.model_validate(item) for item in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/{item_id}", response_model=SharedKnowledgeResponse)
async def get_shared_knowledge(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get a single shared_knowledge by ID."""
    service = SharedKnowledgeService(session)
    try:
        item = await service.get(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return SharedKnowledgeResponse.model_validate(item)


@router.post("", response_model=SharedKnowledgeResponse, status_code=status.HTTP_201_CREATED)
async def create_shared_knowledge(
    payload: SharedKnowledgeCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new shared_knowledge."""
    service = SharedKnowledgeService(session)
    item = await service.create(payload)
    await session.commit()
    return SharedKnowledgeResponse.model_validate(item)


@router.patch("/{item_id}", response_model=SharedKnowledgeResponse)
async def update_shared_knowledge(
    item_id: int,
    payload: SharedKnowledgeUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """Update an existing shared_knowledge."""
    service = SharedKnowledgeService(session)
    try:
        item = await service.update(item_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return SharedKnowledgeResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shared_knowledge(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Delete a shared_knowledge by ID."""
    service = SharedKnowledgeService(session)
    try:
        await service.delete(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return None
