"""Local demo seed for education module (no auth in local env)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.shared_core.config import settings
from apps.api.models.education import Course, Lesson

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/education", tags=["Education"])

DEMO_COURSES = [
    {
        "title": "Climate Basics for Farmers",
        "description": "Intro to climate risk and adaptation.",
        "category": "environmental-science",
        "level": "beginner",
        "duration_hours": 4,
        "instructor": "EcoNojin Academy",
        "lessons": ["What is climate risk", "Local indicators", "Adaptation checklist"],
    },
    {
        "title": "Water-Smart Irrigation",
        "description": "Efficient irrigation and soil moisture.",
        "category": "water-management",
        "level": "intermediate",
        "duration_hours": 6,
        "instructor": "EcoNojin Academy",
        "lessons": ["Soil water balance", "Drip systems", "Scheduling"],
    },
    {
        "title": "Satellite NDVI for Fields",
        "description": "Using satellite vegetation indices.",
        "category": "technology",
        "level": "advanced",
        "duration_hours": 8,
        "instructor": "EcoNojin Academy",
        "lessons": ["NDVI fundamentals", "Cloud masking", "Change detection"],
    },
    {
        "title": "Farm Economics 101",
        "description": "Costs, margins, and simple bookkeeping.",
        "category": "economics",
        "level": "beginner",
        "duration_hours": 5,
        "instructor": "EcoNojin Academy",
        "lessons": ["Cost structure", "Cash flow", "Break-even"],
    },
    {
        "title": "Regenerative Agriculture Practices",
        "description": "Cover crops, rotation, and soil health.",
        "category": "agriculture",
        "level": "intermediate",
        "duration_hours": 7,
        "instructor": "EcoNojin Academy",
        "lessons": ["Soil organic matter", "Cover crops", "Rotation design"],
    },
]


@router.post("/seed-demo")
async def seed_demo(session: AsyncSession = Depends(get_db_session)) -> dict:
    """Insert demo courses when DB is empty. Allowed in local/staging only."""
    if settings.ENVIRONMENT == "production":
        return {"seeded": 0, "message": "disabled in production"}

    total = (await session.execute(select(func.count()).select_from(Course))).scalar_one()
    if total and total > 0:
        return {"seeded": 0, "message": f"already has {total} courses", "total": total}

    seeded = 0
    for c in DEMO_COURSES:
        course = Course(
            title=c["title"],
            description=c["description"],
            category=c["category"],
            level=c["level"],
            duration_hours=c["duration_hours"],
            instructor=c["instructor"],
            is_active=True,
        )
        session.add(course)
        await session.flush()
        for i, title in enumerate(c["lessons"]):
            session.add(
                Lesson(
                    course_id=course.id,
                    title=title,
                    content=None,
                    duration_minutes=20,
                    order=i,
                )
            )
        seeded += 1

    await session.commit()
    logger.info("Seeded %s demo courses", seeded)
    return {"seeded": seeded, "message": "ok"}
