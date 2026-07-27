"""Education repository — async queries with explicit relationship loading."""

from __future__ import annotations

import logging
from typing import List, Optional

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.api.models.education import Course, Enrollment, Lesson
from apps.api.schemas.education import CourseCreate, CourseUpdate

logger = logging.getLogger(__name__)

_SORTABLE = {
    "id": Course.id,
    "title": Course.title,
    "created_at": Course.created_at,
    "updated_at": Course.updated_at,
    "duration_hours": Course.duration_hours,
}


class EducationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _course_options(self):
        return (
            selectinload(Course.lessons),
            selectinload(Course.enrollments),
        )

    def _apply_sort(self, query, sort: Optional[str]):
        if not sort:
            return query.order_by(desc(Course.id))
        direction = desc if sort.startswith("-") else asc
        key = sort[1:] if sort.startswith("-") else sort
        col = _SORTABLE.get(key, Course.id)
        return query.order_by(direction(col))

    async def get_course_by_id(self, course_id: int) -> Optional[Course]:
        result = await self.session.execute(
            select(Course).where(Course.id == course_id).options(*self._course_options())
        )
        return result.scalar_one_or_none()

    async def list_courses(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None,
        level: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> tuple[List[Course], int]:
        query = select(Course).options(*self._course_options())

        if search:
            term = f"%{search.lower()}%"
            query = query.where(
                (Course.title.ilike(term))
                | (Course.description.ilike(term))
                | (Course.instructor.ilike(term))
            )
        if category:
            query = query.where(Course.category == category)
        if level:
            query = query.where(Course.level == level)

        count_query = select(func.count()).select_from(Course)
        if search:
            term = f"%{search.lower()}%"
            count_query = count_query.where(
                (Course.title.ilike(term))
                | (Course.description.ilike(term))
                | (Course.instructor.ilike(term))
            )
        if category:
            count_query = count_query.where(Course.category == category)
        if level:
            count_query = count_query.where(Course.level == level)

        total = (await self.session.execute(count_query)).scalar_one()
        query = self._apply_sort(query, sort).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().unique().all()), int(total)

    async def create_course(self, data: CourseCreate) -> Course:
        obj = Course(**data.model_dump(exclude={"lessons"}))
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update_course(self, course_id: int, data: CourseUpdate) -> Optional[Course]:
        obj = await self.get_course_by_id(course_id)
        if not obj:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        await self.session.flush()
        return await self.get_course_by_id(course_id)

    async def delete_course(self, course_id: int) -> bool:
        obj = await self.get_course_by_id(course_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def get_lesson_by_id(self, lesson_id: int) -> Optional[Lesson]:
        result = await self.session.execute(select(Lesson).where(Lesson.id == lesson_id))
        return result.scalar_one_or_none()

    async def list_lessons_by_course(
        self, course_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[List[Lesson], int]:
        q = (
            select(Lesson)
            .where(Lesson.course_id == course_id)
            .order_by(Lesson.order)
            .offset(skip)
            .limit(limit)
        )
        items = list((await self.session.execute(q)).scalars().all())
        total = (
            await self.session.execute(
                select(func.count()).select_from(Lesson).where(Lesson.course_id == course_id)
            )
        ).scalar_one()
        return items, int(total)

    async def create_lesson(self, course_id: int, data: dict) -> Lesson:
        obj = Lesson(course_id=course_id, **data)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update_lesson(self, lesson_id: int, data: dict) -> Optional[Lesson]:
        from apps.api.schemas.education import LessonUpdate

        obj = await self.get_lesson_by_id(lesson_id)
        if not obj:
            return None
        for key, value in LessonUpdate(**data).model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete_lesson(self, lesson_id: int) -> bool:
        obj = await self.get_lesson_by_id(lesson_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def get_enrollment_by_id(self, enrollment_id: int) -> Optional[Enrollment]:
        result = await self.session.execute(
            select(Enrollment).where(Enrollment.id == enrollment_id)
        )
        return result.scalar_one_or_none()

    async def list_enrollments_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[List[Enrollment], int]:
        q = (
            select(Enrollment)
            .where(Enrollment.user_id == user_id)
            .order_by(Enrollment.enrolled_at.desc())
            .offset(skip)
            .limit(limit)
        )
        items = list((await self.session.execute(q)).scalars().all())
        total = (
            await self.session.execute(
                select(func.count()).select_from(Enrollment).where(Enrollment.user_id == user_id)
            )
        ).scalar_one()
        return items, int(total)

    async def get_user_enrollment(self, course_id: int, user_id: int) -> Optional[Enrollment]:
        result = await self.session.execute(
            select(Enrollment).where(
                Enrollment.course_id == course_id,
                Enrollment.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_enrollment(self, course_id: int, user_id: int) -> Enrollment:
        obj = Enrollment(course_id=course_id, user_id=user_id)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update_enrollment(self, enrollment_id: int, data: dict) -> Optional[Enrollment]:
        from apps.api.schemas.education import EnrollmentUpdate

        obj = await self.get_enrollment_by_id(enrollment_id)
        if not obj:
            return None
        for key, value in EnrollmentUpdate(**data).model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete_enrollment(self, enrollment_id: int) -> bool:
        obj = await self.get_enrollment_by_id(enrollment_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def get_stats(self) -> dict:
        total_courses = (
            await self.session.execute(select(func.count()).select_from(Course))
        ).scalar_one()
        total_lessons = (
            await self.session.execute(select(func.count()).select_from(Lesson))
        ).scalar_one()
        total_enrollments = (
            await self.session.execute(select(func.count()).select_from(Enrollment))
        ).scalar_one()

        by_category: dict[str, int] = {}
        for cat in (
            "agriculture",
            "water-management",
            "environmental-science",
            "economics",
            "technology",
        ):
            by_category[cat] = (
                await self.session.execute(
                    select(func.count()).select_from(Course).where(Course.category == cat)
                )
            ).scalar_one()

        by_level: dict[str, int] = {}
        for lvl in ("beginner", "intermediate", "advanced"):
            by_level[lvl] = (
                await self.session.execute(
                    select(func.count()).select_from(Course).where(Course.level == lvl)
                )
            ).scalar_one()

        return {
            "total_courses": int(total_courses),
            "total_lessons": int(total_lessons),
            "total_enrollments": int(total_enrollments),
            "by_category": by_category,
            "by_level": by_level,
        }
