"""Standard list envelope (R13/R14)."""

from __future__ import annotations

from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageMeta(BaseModel):
    total: int = 0
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=200)
    pages: int = 0


class Page(BaseModel, Generic[T]):
    data: Sequence[T]
    meta: PageMeta


def page_params(page: int = 1, size: int = 20) -> tuple[int, int, int]:
    """Return page, size, skip."""
    page = max(1, int(page))
    size = min(200, max(1, int(size)))
    skip = (page - 1) * size
    return page, size, skip


def build_page(items: Sequence[T], total: int, page: int, size: int) -> dict:
    pages = (total + size - 1) // size if size else 0
    return {
        "data": list(items),
        "meta": {
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
        },
    }
