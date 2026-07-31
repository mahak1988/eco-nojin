"""Agriculture schools API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.schemas.agriculture_school import (
    AgricultureSchoolCreate,
    AgricultureSchoolListResponse,
    AgricultureSchoolResponse,
    AgricultureSchoolUpdate,
    SchoolStats,
)
from apps.api.services.agriculture_school import AgricultureSchoolService
from apps.shared_core.database.session import get_db_session
from apps.shared_core.deps import require_write_auth

router = APIRouter(prefix="/api/v1/agriculture-schools", tags=["Agriculture Schools"])


@router.get("/", response_model=AgricultureSchoolListResponse)
async def list_schools(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    school_type: str | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
) -> AgricultureSchoolListResponse:
    service = AgricultureSchoolService(session)
    schools, total = await service.list(skip, limit, search, school_type)
    items = [AgricultureSchoolResponse.model_validate(s) for s in schools]
    return AgricultureSchoolListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/stats", response_model=SchoolStats)
async def get_stats(session: AsyncSession = Depends(get_db_session)) -> SchoolStats:
    service = AgricultureSchoolService(session)
    return SchoolStats(**await service.get_stats())


@router.post("/", response_model=AgricultureSchoolResponse, status_code=status.HTTP_201_CREATED)
async def create_school(
    payload: AgricultureSchoolCreate,
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> AgricultureSchoolResponse:
    service = AgricultureSchoolService(session)
    school = await service.create(payload)
    return AgricultureSchoolResponse.model_validate(school)


@router.get("/{school_id}", response_model=AgricultureSchoolResponse)
async def get_school(
    school_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> AgricultureSchoolResponse:
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
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> AgricultureSchoolResponse:
    service = AgricultureSchoolService(session)
    try:
        school = await service.update(school_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return AgricultureSchoolResponse.model_validate(school)


@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_school(
    school_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_write_auth),
) -> None:
    service = AgricultureSchoolService(session)
    try:
        await service.delete(school_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
