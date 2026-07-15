"""
simulation router | روتر simulation
=================================
FastAPI router exposing simulation endpoints.

Endpoints:
    GET    /simulation          List with pagination
    GET    /simulation/{id}    Get by ID
    POST   /simulation          Create
    PATCH  /simulation/{id}    Update
    DELETE /simulation/{id}    Delete
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

from apps.simulation.schemas import (
    SimulationCreate,
    SimulationUpdate,
    SimulationResponse,
    SimulationListResponse,
)
from apps.simulation.service import SimulationService

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.get("", response_model=SimulationListResponse)
async def list_simulation(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
):
    """List simulation records with pagination."""
    service = SimulationService(session)
    items, total = await service.list(skip=skip, limit=limit)
    return SimulationListResponse(
        items=[SimulationResponse.model_validate(item) for item in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/{item_id}", response_model=SimulationResponse)
async def get_simulation(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get a single simulation by ID."""
    service = SimulationService(session)
    try:
        item = await service.get(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return SimulationResponse.model_validate(item)


@router.post("", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
async def create_simulation(
    payload: SimulationCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new simulation."""
    service = SimulationService(session)
    item = await service.create(payload)
    await session.commit()
    return SimulationResponse.model_validate(item)


@router.patch("/{item_id}", response_model=SimulationResponse)
async def update_simulation(
    item_id: int,
    payload: SimulationUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """Update an existing simulation."""
    service = SimulationService(session)
    try:
        item = await service.update(item_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return SimulationResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_simulation(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Delete a simulation by ID."""
    service = SimulationService(session)
    try:
        await service.delete(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return None
