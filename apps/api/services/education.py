"""Education service — business rules."""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.education import Course, Enrollment, Lesson
from apps.api.repositories.education import EducationRepository
from apps.api.schemas.education import (
    CourseCreate,
    CourseUpdate,
    EnrollmentUpdate,
    LessonCreate,
    LessonUpdate,
)
from apps.shared_core.schemas.pagination import page_to_offset

logger = logging.getLogger(__name__)


class EducationService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = EducationRepository(session)

    async def list_courses(
        self,
        *,
        page: int = 1,
        size: int = 20,
        skip: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        category: str | None = None,
        level: str | None = None,
        sort: str | None = "-id",
    ) -> tuple[list[Course], int, int, int]:
        """Returns (items, total, page, size). Prefer page/size (R13); skip/limit legacy."""
        size = min(limit if limit is not None else size, 200)
        size = max(1, size)
        if skip is not None:
            # legacy offset
            offset = max(0, skip)
            page = (offset // size) + 1 if size else 1
        else:
            page = max(1, page)
            offset = page_to_offset(page, size)
        items, total = await self.repo.list_courses(
            offset, size, search, category, level, sort=sort
        )
        return items, total, page, size

    async def create_course(self, data: CourseCreate) -> Course:
        return await self.repo.create_course(data)

    async def get_course(self, course_id: int) -> Course:
        obj = await self.repo.get_course_by_id(course_id)
        if not obj:
            raise ValueError(f"Course with id={course_id} not found")
        return obj

    async def update_course(self, course_id: int, data: CourseUpdate) -> Course:
        obj = await self.repo.update_course(course_id, data)
        if not obj:
            raise ValueError(f"Course with id={course_id} not found")
        return obj

    async def delete_course(self, course_id: int) -> None:
        if not await self.repo.delete_course(course_id):
            raise ValueError(f"Course with id={course_id} not found")

    async def list_lessons(
        self, course_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[list[Lesson], int]:
        return await self.repo.list_lessons_by_course(course_id, skip, limit)

    async def create_lesson(self, course_id: int, data: LessonCreate) -> Lesson:
        await self.get_course(course_id)
        return await self.repo.create_lesson(course_id, data.model_dump())

    async def get_lesson(self, lesson_id: int) -> Lesson:
        obj = await self.repo.get_lesson_by_id(lesson_id)
        if not obj:
            raise ValueError(f"Lesson with id={lesson_id} not found")
        return obj

    async def update_lesson(self, lesson_id: int, data: LessonUpdate) -> Lesson:
        obj = await self.repo.update_lesson(lesson_id, data.model_dump())
        if not obj:
            raise ValueError(f"Lesson with id={lesson_id} not found")
        return obj

    async def delete_lesson(self, lesson_id: int) -> None:
        if not await self.repo.delete_lesson(lesson_id):
            raise ValueError(f"Lesson with id={lesson_id} not found")

    async def list_enrollments(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[list[Enrollment], int]:
        return await self.repo.list_enrollments_by_user(user_id, skip, limit)

    async def create_enrollment(self, course_id: int, user_id: int) -> Enrollment:
        existing = await self.repo.get_user_enrollment(course_id, user_id)
        if existing:
            raise ValueError("User already enrolled in this course")
        return await self.repo.create_enrollment(course_id, user_id)

    async def update_enrollment(self, enrollment_id: int, data: EnrollmentUpdate) -> Enrollment:
        obj = await self.repo.update_enrollment(enrollment_id, data.model_dump())
        if not obj:
            raise ValueError(f"Enrollment with id={enrollment_id} not found")
        return obj

    async def delete_enrollment(self, enrollment_id: int) -> None:
        if not await self.repo.delete_enrollment(enrollment_id):
            raise ValueError(f"Enrollment with id={enrollment_id} not found")

    async def get_stats(self) -> dict:
        return await self.repo.get_stats()
