"""
Education System Tests
=======================
Tests for Course, Lesson, Enrollment CRUD operations.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.education import Course, Lesson, Enrollment, CourseCategory, DifficultyLevel
from apps.api.schemas.education import CourseCreate, LessonCreate, EnrollmentCreate


@pytest.fixture
async def education_db_session():
    """Create a test database session for education models."""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from apps.shared_core.database.session import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_course_crud(education_db_session: AsyncSession):
    """Test course CRUD operations."""
    # Create
    course = Course(
        id="course-1",
        title="Introduction to Agriculture",
        description="Learn the basics of agriculture",
        category=CourseCategory.AGRICULTURE,
        level=DifficultyLevel.BEGINNER,
        instructor_id="instructor-1",
        duration_hours=10,
    )
    education_db_session.add(course)
    await education_db_session.flush()

    # Read
    result = await education_db_session.execute(select(Course).where(Course.id == "course-1"))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.title == "Introduction to Agriculture"
    assert fetched.category == CourseCategory.AGRICULTURE

    # Update
    fetched.duration_hours = 15
    await education_db_session.flush()

    result = await education_db_session.execute(select(Course).where(Course.id == "course-1"))
    updated = result.scalar_one()
    assert updated.duration_hours == 15

    # Delete
    await education_db_session.delete(updated)
    await education_db_session.flush()

    result = await education_db_session.execute(select(Course).where(Course.id == "course-1"))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_lesson_crud(education_db_session: AsyncSession):
    """Test lesson CRUD operations."""
    # Create course first
    course = Course(
        id="course-2",
        title="Test Course",
        category=CourseCategory.SCIENCE,
        level=DifficultyLevel.INTERMEDIATE,
    )
    education_db_session.add(course)
    await education_db_session.flush()

    # Create lesson
    lesson = Lesson(
        id="lesson-1",
        title="Soil Basics",
        content="Understanding soil composition",
        course_id="course-2",
        order=1,
        duration_minutes=30,
    )
    education_db_session.add(lesson)
    await education_db_session.flush()

    # Read
    result = await education_db_session.execute(select(Lesson).where(Lesson.id == "lesson-1"))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.title == "Soil Basics"
    assert fetched.course_id == "course-2"


@pytest.mark.asyncio
async def test_enrollment_crud(education_db_session: AsyncSession):
    """Test enrollment CRUD operations."""
    # Create course and user
    course = Course(
        id="course-3",
        title="Enrollment Test Course",
        category=CourseCategory.TECHNOLOGY,
        level=DifficultyLevel.BEGINNER,
    )
    education_db_session.add(course)
    await education_db_session.flush()

    # Create enrollment
    enrollment = Enrollment(
        id="enroll-1",
        user_id="user-1",
        course_id="course-3",
        progress=0.5,
    )
    education_db_session.add(enrollment)
    await education_db_session.flush()

    # Read
    result = await education_db_session.execute(select(Enrollment).where(Enrollment.id == "enroll-1"))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.progress == 0.5

    # Update progress
    fetched.progress = 1.0
    await education_db_session.flush()

    result = await education_db_session.execute(select(Enrollment).where(Enrollment.id == "enroll-1"))
    updated = result.scalar_one()
    assert updated.progress == 1.0


@pytest.mark.asyncio
async def test_course_category_enum():
    """Test course category enum values."""
    assert CourseCategory.AGRICULTURE == "agriculture"
    assert CourseCategory.SCIENCE == "science"
    assert CourseCategory.TECHNOLOGY == "technology"


@pytest.mark.asyncio
async def test_difficulty_level_enum():
    """Test difficulty level enum values."""
    assert DifficultyLevel.BEGINNER == "beginner"
    assert DifficultyLevel.INTERMEDIATE == "intermediate"
    assert DifficultyLevel.ADVANCED == "advanced"