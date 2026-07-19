"""
Education Router - Database backed
==================================
RESTful endpoints for educational content and courses.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.api.schemas.education import (
    CourseCreate, CourseUpdate,
    CourseResponse, CourseListResponse, CourseStats,
    LessonCreate, LessonUpdate,
    LessonResponse,
    EnrollmentCreate, EnrollmentUpdate,
    EnrollmentResponse
)
from apps.api.services.education import EducationService

router = APIRouter(prefix="/api/v1/education", tags=["📚 Education"])


# ==================== Courses ====================

@router.get("/courses", response_model=CourseListResponse)
async def list_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None, description="Search by title, description, or instructor"),
    category: Optional[str] = Query(None, description="Filter by category"),
    level: Optional[str] = Query(None, description="Filter by level"),
    session: AsyncSession = Depends(get_db_session)
) -> CourseListResponse:
    """List courses with optional search and filtering."""
    service = EducationService(session)
    courses, total = await service.list_courses(skip, limit, search, category, level)
    return CourseListResponse(items=courses, total=total, skip=skip, limit=limit)


@router.get("/courses/stats", response_model=CourseStats)
async def get_course_stats(session: AsyncSession = Depends(get_db_session)) -> CourseStats:
    """Get statistics about courses."""
    service = EducationService(session)
    stats = await service.get_stats()
    return CourseStats(**stats)


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: CourseCreate,
    session: AsyncSession = Depends(get_db_session)
) -> CourseResponse:
    """Create a new course."""
    service = EducationService(session)
    course = await service.create_course(payload)
    await session.commit()
    return CourseResponse.model_validate(course)


@router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> CourseResponse:
    """Get a specific course by ID."""
    service = EducationService(session)
    try:
        course = await service.get_course(course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return CourseResponse.model_validate(course)


@router.patch("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    payload: CourseUpdate,
    session: AsyncSession = Depends(get_db_session)
) -> CourseResponse:
    """Update an existing course."""
    service = EducationService(session)
    try:
        course = await service.update_course(course_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return CourseResponse.model_validate(course)


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> None:
    """Delete a course."""
    service = EducationService(session)
    try:
        await service.delete_course(course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()


# ==================== Lessons ====================

@router.get("/courses/{course_id}/lessons", response_model=list[LessonResponse])
async def list_lessons(
    course_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session)
) -> list[LessonResponse]:
    """List lessons for a specific course."""
    service = EducationService(session)
    lessons, _ = await service.list_lessons(course_id, skip, limit)
    return [LessonResponse.model_validate(l) for l in lessons]


@router.post("/courses/{course_id}/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    course_id: int,
    payload: LessonCreate,
    session: AsyncSession = Depends(get_db_session)
) -> LessonResponse:
    """Create a new lesson within a course."""
    service = EducationService(session)
    try:
        lesson = await service.create_lesson(course_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return LessonResponse.model_validate(lesson)


@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> LessonResponse:
    """Get a specific lesson by ID."""
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
    session: AsyncSession = Depends(get_db_session)
) -> LessonResponse:
    """Update an existing lesson."""
    service = EducationService(session)
    try:
        lesson = await service.update_lesson(lesson_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return LessonResponse.model_validate(lesson)


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> None:
    """Delete a lesson."""
    service = EducationService(session)
    try:
        await service.delete_lesson(lesson_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()


# ==================== Enrollments ====================

@router.get("/users/{user_id}/enrollments", response_model=list[EnrollmentResponse])
async def list_enrollments(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session)
) -> list[EnrollmentResponse]:
    """List enrollments for a specific user."""
    service = EducationService(session)
    enrollments, _ = await service.list_enrollments(user_id, skip, limit)
    return [EnrollmentResponse.model_validate(e) for e in enrollments]


@router.post("/courses/{course_id}/enroll", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    course_id: int,
    user_id: int = Query(..., description="User ID to enroll"),
    session: AsyncSession = Depends(get_db_session)
) -> EnrollmentResponse:
    """Enroll a user in a course."""
    service = EducationService(session)
    try:
        enrollment = await service.create_enrollment(course_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await session.commit()
    return EnrollmentResponse.model_validate(enrollment)


@router.patch("/enrollments/{enrollment_id}", response_model=EnrollmentResponse)
async def update_enrollment(
    enrollment_id: int,
    payload: EnrollmentUpdate,
    session: AsyncSession = Depends(get_db_session)
) -> EnrollmentResponse:
    """Update an enrollment (e.g., progress)."""
    service = EducationService(session)
    try:
        enrollment = await service.update_enrollment(enrollment_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return EnrollmentResponse.model_validate(enrollment)


@router.delete("/enrollments/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(
    enrollment_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> None:
    """Remove an enrollment."""
    service = EducationService(session)
    try:
        await service.delete_enrollment(enrollment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()