"""Standard list pagination helpers (R13/R14).

Backward-compatible exports used by farms/crops/education/inventory routers:
  ListMeta, ListEnvelope, build_meta, page_to_offset
"""

from __future__ import annotations

from math import ceil
from typing import Any, Generic, Sequence, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ListMeta(BaseModel):
    """Legacy + current list metadata."""

    total: int = Field(0, ge=0)
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=200)
    pages: int = Field(0, ge=0)


# Alias for newer code
PageMeta = ListMeta


class ListEnvelope(BaseModel, Generic[T]):
    data: Sequence[T]
    meta: ListMeta


Page = ListEnvelope


def page_to_offset(page: int = 1, size: int = 20) -> tuple[int, int, int]:
    """Return (page, size, offset/skip)."""
    page = max(1, int(page or 1))
    size = min(200, max(1, int(size or 20)))
    offset = (page - 1) * size
    return page, size, offset


def page_params(page: int = 1, size: int = 20) -> tuple[int, int, int]:
    return page_to_offset(page, size)


def build_meta(total: int, page: int, size: int) -> ListMeta:
    total = max(0, int(total))
    page = max(1, int(page))
    size = max(1, int(size))
    pages = ceil(total / size) if size > 0 and total > 0 else (0 if total == 0 else 1)
    return ListMeta(total=total, page=page, size=size, pages=pages)


def build_page(items: Sequence[Any], total: int, page: int, size: int) -> dict[str, Any]:
    meta = build_meta(total, page, size)
    return {"data": list(items), "meta": meta.model_dump()}
