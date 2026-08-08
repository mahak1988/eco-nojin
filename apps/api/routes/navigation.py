"""
Navigation API routes for dynamic header and topic categories.
"""

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import distinct
from sqlalchemy.orm import Session

from apps.api.models.education import CourseCategory
from apps.api.models.library import LibraryResource
from apps.shared_core.database.session import get_db

router = APIRouter(prefix="/navigation", tags=["Navigation"])


class NavigationItem(BaseModel):
    id: str
    title: str
    slug: str
    url: str
    source: str
    order: int
    isActive: bool
    count: int | None = None


class HeaderNavigationResponse(BaseModel):
    primaryMenu: list[NavigationItem]
    topicCategories: list[NavigationItem]
    meta: dict[str, Any]


def _generate_slug(title: str) -> str:
    """Convert Persian/English title to URL-friendly slug."""
    # Simple slug generation - could be enhanced
    import re

    slug = re.sub(r"[^\w\s\u0600-\u06FF]", " ", title)
    slug = re.sub(r"\s+", "-", slug).lower()
    return slug.strip("-")


@router.get("/header", response_model=HeaderNavigationResponse)
def get_header_navigation(db: Session = Depends(get_db)):
    """
    Get dynamic header navigation including primary menu and topic categories.
    Provides graceful degradation if individual data sources fail.
    """
    primary_menu = [
        NavigationItem(
            id="home", title="Home", slug="home", url="/", source="static", order=0, isActive=True
        ),
        NavigationItem(
            id="courses",
            title="Courses",
            slug="courses",
            url="/education",
            source="static",
            order=1,
            isActive=True,
        ),
        NavigationItem(
            id="library",
            title="Library",
            slug="library",
            url="/library",
            source="static",
            order=2,
            isActive=True,
        ),
    ]

    topic_categories = []
    failed_sources = []
    degraded = False

    # Fetch Course Categories
    try:
        course_categories = db.query(CourseCategory).distinct().all()
        for idx, category in enumerate(course_categories):
            slug = _generate_slug(category.value)
            topic_categories.append(
                NavigationItem(
                    id=f"course:{category.value}",
                    title=category.value.replace("-", " ").replace("_", " ").title(),
                    slug=slug,
                    url=f"/education?category={slug}",
                    source="course",
                    order=idx,
                    isActive=True,
                )
            )
    except Exception as e:
        failed_sources.append(f"course_categories: {e!s}")
        degraded = True

    # Fetch Library Resource Categories
    try:
        library_categories = db.query(distinct(LibraryResource.category)).all()
        for idx, (cat,) in enumerate(library_categories):
            slug = _generate_slug(cat)
            # Check for duplicate slugs and add prefix if needed
            full_slug = slug
            if any(item.slug == full_slug for item in topic_categories):
                full_slug = f"library-{slug}"
            topic_categories.append(
                NavigationItem(
                    id=f"library:{cat}",
                    title=cat.replace("-", " ").replace("_", " ").title(),
                    slug=full_slug,
                    url=f"/library?category={full_slug}",
                    source="library",
                    order=len(course_categories) + idx if "course_categories" in locals() else idx,
                    isActive=True,
                )
            )
    except Exception as e:
        failed_sources.append(f"library_categories: {e!s}")
        degraded = True

    # Sort topic categories by order
    topic_categories.sort(key=lambda x: x.order)

    meta = {
        "degraded": degraded,
        "sources": ["CourseCategory", "LibraryResource"],
        "failedSources": failed_sources if failed_sources else None,
    }

    return HeaderNavigationResponse(
        primaryMenu=primary_menu, topicCategories=topic_categories, meta=meta
    )
