"""
Agriculture Schools Router - Database backed
==========================================
RESTful endpoints for agricultural education institutions.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.api.schemas.agriculture_school import (
    AgricultureSchoolCreate, AgricultureSchoolUpdate,
    AgricultureSchoolResponse, AgricultureSchoolListResponse, SchoolStats
)
from apps.api.services.agriculture_school import AgricultureSchoolService

router = APIRouter(prefix="/api/v1/agriculture-schools", tags=["🏯 Agriculture Schools"])


@router.get("/", response_model=AgricultureSchoolListResponse)
async def list_schools(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None, description="Search by name, province, or city"),
    school_type: Optional[str] = Query(None, pattern="^(university|institute|training-center)$"),
    session: AsyncSession = Depends(get_db_session)
) -> AgricultureSchoolListResponse:
    """List agriculture schools with optional search and filtering."""
    service = AgricultureSchoolService(session)
    schools, total = await service.list(skip, limit, search, school_type)
    
    # Transform to response format
    items = [AgricultureSchoolResponse.model_validate(s) for s in schools]
    
    return AgricultureSchoolListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/stats", response_model=SchoolStats)
async def get_stats(session: AsyncSession = Depends(get_db_session)) -> SchoolStats:
    """Get statistics about agriculture schools."""
    service = AgricultureSchoolService(session)
    stats = await service.get_stats()
    return SchoolStats(**stats)


@router.post("/", response_model=AgricultureSchoolResponse, status_code=status.HTTP_201_CREATED)
async def create_school(
    payload: AgricultureSchoolCreate,
    session: AsyncSession = Depends(get_db_session)
) -> AgricultureSchoolResponse:
    """Create a new agriculture school."""
    service = AgricultureSchoolService(session)
    school = await service.create(payload)
    await session.commit()
    return AgricultureSchoolResponse.model_validate(school)


@router.get("/{school_id}", response_model=AgricultureSchoolResponse)
async def get_school(
    school_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> AgricultureSchoolResponse:
    """Get a specific agriculture school by ID."""
    service = AgricultureSchoolService(session)
    try:
        school = await service.get(school_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return AgricultureSchoolResponse.model_validate(school)


@router.patch("/{school_id}", response_model=AgricultureSchoolResponse)
async def update_school(
    school_id: int,
    payload: AgricultureSchoolUpdate,
    session: AsyncSession = Depends(get_db_session)
) -> AgricultureSchoolResponse:
    """Update an existing agriculture school."""
    service = AgricultureSchoolService(session)
    try:
        school = await service.update(school_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return AgricultureSchoolResponse.model_validate(school)


@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_school(
    school_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> None:
    """Delete an agriculture school."""
    service = AgricultureSchoolService(session)
    try:
        await service.delete(school_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()