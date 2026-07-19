"""
Education Repository
====================
Data access layer — all database queries live here.
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.education import Course, Lesson, Enrollment
from apps.api.schemas.education import CourseCreate, CourseUpdate


class EducationRepository:
    """Repository for Education entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ==================== Course Operations ====================

    async def get_course_by_id(self, course_id: int) -> Optional[Course]:
        result = await self.session.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalar_one_or_none()

    async def list_courses(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None,
        level: Optional[str] = None
    ) -> tuple[List[Course], int]:
        query = select(Course)

        if search:
            search_term = f"%{search.lower()}%"
            query = query.where(
                (Course.title.ilike(search_term)) |
                (Course.description.ilike(search_term)) |
                (Course.instructor.ilike(search_term))
            )

        if category:
            query = query.where(Course.category == category)

        if level:
            query = query.where(Course.level == level)

        query = query.order_by(Course.title).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        count_query = select(func.count()).select_from(Course)
        if search:
            search_term = f"%{search.lower()}%"
            count_query = count_query.where(
                (Course.title.ilike(search_term)) |
                (Course.description.ilike(search_term)) |
                (Course.instructor.ilike(search_term))
            )
        if category:
            count_query = count_query.where(Course.category == category)
        if level:
            count_query = count_query.where(Course.level == level)

        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return items, total

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

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)

        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete_course(self, course_id: int) -> bool:
        obj = await self.get_course_by_id(course_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    # ==================== Lesson Operations ====================

    async def get_lesson_by_id(self, lesson_id: int) -> Optional[Lesson]:
        result = await self.session.execute(
            select(Lesson).where(Lesson.id == lesson_id)
        )
        return result.scalar_one_or_none()

    async def list_lessons_by_course(
        self, course_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[List[Lesson], int]:
        query = select(Lesson).where(Lesson.course_id == course_id)
        query = query.order_by(Lesson.order).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        count_query = select(func.count()).select_from(Lesson).where(Lesson.course_id == course_id)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return items, total

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

        update_schema = LessonUpdate(**data)
        update_data = update_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
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

    # ==================== Enrollment Operations ====================

    async def get_enrollment_by_id(self, enrollment_id: int) -> Optional[Enrollment]:
        result = await self.session.execute(
            select(Enrollment).where(Enrollment.id == enrollment_id)
        )
        return result.scalar_one_or_none()

    async def list_enrollments_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[List[Enrollment], int]:
        query = select(Enrollment).where(Enrollment.user_id == user_id)
        query = query.order_by(Enrollment.enrolled_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        count_query = select(func.count()).select_from(Enrollment).where(Enrollment.user_id == user_id)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return items, total

    async def get_user_enrollment(self, course_id: int, user_id: int) -> Optional[Enrollment]:
        result = await self.session.execute(
            select(Enrollment).where(
                Enrollment.course_id == course_id,
                Enrollment.user_id == user_id
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

        update_schema = EnrollmentUpdate(**data)
        update_data = update_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
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
        result = await self.session.execute(select(Course))
        courses = result.scalars().all()

        lessons_result = await self.session.execute(select(Lesson))
        lessons = lessons_result.scalars().all()

        enrollments_result = await self.session.execute(select(Enrollment))
        enrollments = enrollments_result.scalars().all()

        return {
            "total_courses": len(courses),
            "total_lessons": len(lessons),
            "total_enrollments": len(enrollments),
            "by_category": {
                cat: len([c for c in courses if c.category == cat])
                for cat in ["agriculture", "water-management", "environmental-science", "economics", "technology"]
            },
            "by_level": {
                lvl: len([c for c in courses if c.level == lvl])
                for lvl in ["beginner", "intermediate", "advanced"]
            }
        }