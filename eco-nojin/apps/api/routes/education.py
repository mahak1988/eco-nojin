"""Education API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.schemas.education import (
    CourseCreate,
    CourseListResponse,
    CourseResponse,
    CourseStats,
    CourseUpdate,
    EnrollmentResponse,
    EnrollmentUpdate,
    LessonCreate,
    LessonResponse,
    LessonUpdate,
)
from apps.api.services.education import EducationService
from apps.shared_core.database.session import get_db_session
from apps.shared_core.rbac import require_permission
from apps.shared_core.schemas.pagination import build_meta

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/education", tags=["Education"])


def _course_to_response(course) -> CourseResponse:
    lessons = getattr(course, "lessons", None) or []
    enrollments = getattr(course, "enrollments", None) or []
    return CourseResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        category=course.category,
        level=course.level,
        duration_hours=course.duration_hours or 0,
        instructor=course.instructor,
        is_active=bool(course.is_active),
        created_at=course.created_at,
        updated_at=course.updated_at,
        lessons=[LessonResponse.model_validate(x) for x in lessons],
        enrollments=[EnrollmentResponse.model_validate(x) for x in enrollments],
    )


@router.get("/courses", response_model=CourseListResponse)
async def list_courses(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    sort: str = Query("-id"),
    skip: int | None = Query(None, ge=0),
    limit: int | None = Query(None, ge=1, le=200),
    search: str | None = Query(None),
    category: str | None = Query(None),
    level: str | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
) -> CourseListResponse:
    service = EducationService(session)
    courses, total, page_out, size_out = await service.list_courses(
        page=page,
        size=size,
        skip=skip,
        limit=limit,
        search=search,
        category=category,
        level=level,
        sort=sort,
    )
    items = [_course_to_response(c) for c in courses]
    meta = build_meta(total, page_out, size_out)
    return CourseListResponse(
        data=items,
        meta=meta,
        items=items,
        total=total,
        skip=(page_out - 1) * size_out,
        limit=size_out,
    )


@router.get("/courses/stats", response_model=CourseStats)
async def get_course_stats(
    session: AsyncSession = Depends(get_db_session),
) -> CourseStats:
    service = EducationService(session)
    return CourseStats(**await service.get_stats())


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: CourseCreate,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("education:write")),
) -> CourseResponse:
    service = EducationService(session)
    course = await service.create_course(payload)
    course = await service.get_course(course.id)
    return _course_to_response(course)


@router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> CourseResponse:
    service = EducationService(session)
    try:
        course = await service.get_course(course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return _course_to_response(course)


@router.patch("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    payload: CourseUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("education:write")),
) -> CourseResponse:
    service = EducationService(session)
    try:
        course = await service.update_course(course_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return _course_to_response(course)


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("education:write")),
) -> None:
    service = EducationService(session)
    try:
        await service.delete_course(course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/courses/{course_id}/lessons", response_model=list[LessonResponse])
async def list_lessons(
    course_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
) -> list[LessonResponse]:
    service = EducationService(session)
    lessons, _ = await service.list_lessons(course_id, skip, limit)
    return [LessonResponse.model_validate(l) for l in lessons]


@router.post(
    "/courses/{course_id}/lessons",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_lesson(
    course_id: int,
    payload: LessonCreate,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("education:write")),
) -> LessonResponse:
    service = EducationService(session)
    try:
        lesson = await service.create_lesson(course_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return LessonResponse.model_validate(lesson)


@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> LessonResponse:
    service = EducationService(session)
    try:
        lesson = await service.get_lesson(lesson_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return LessonResponse.model_validate(lesson)


@router.patch("/lessons/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: int,
    payload: LessonUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("education:write")),
) -> LessonResponse:
    service = EducationService(session)
    try:
        lesson = await service.update_lesson(lesson_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return LessonResponse.model_validate(lesson)


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("education:write")),
) -> None:
    service = EducationService(session)
    try:
        await service.delete_lesson(lesson_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/users/{user_id}/enrollments", response_model=list[EnrollmentResponse])
async def list_enrollments(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
) -> list[EnrollmentResponse]:
    service = EducationService(session)
    enrollments, _ = await service.list_enrollments(user_id, skip, limit)
    return [EnrollmentResponse.model_validate(e) for e in enrollments]


@router.post(
    "/courses/{course_id}/enroll",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def enroll_in_course(
    course_id: int,
    user_id: int = Query(...),
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("education:write")),
) -> EnrollmentResponse:
    service = EducationService(session)
    try:
        enrollment = await service.create_enrollment(course_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return EnrollmentResponse.model_validate(enrollment)


@router.patch("/enrollments/{enrollment_id}", response_model=EnrollmentResponse)
async def update_enrollment(
    enrollment_id: int,
    payload: EnrollmentUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("education:write")),
) -> EnrollmentResponse:
    service = EducationService(session)
    try:
        enrollment = await service.update_enrollment(enrollment_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return EnrollmentResponse.model_validate(enrollment)


@router.delete("/enrollments/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(
    enrollment_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("education:write")),
) -> None:
    service = EducationService(session)
    try:
        await service.delete_enrollment(enrollment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
