"""R13/R14 shared pagination and list envelope."""

from __future__ import annotations

from math import ceil
from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ListMeta(BaseModel):
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    pages: int = Field(..., ge=0)
    size: int = Field(..., ge=1)


class ListEnvelope(BaseModel, Generic[T]):
    """Canonical list response (R14)."""

    data: List[T]
    meta: ListMeta


def page_to_offset(page: int, size: int) -> int:
    return max(0, (page - 1) * size)


def build_meta(total: int, page: int, size: int) -> ListMeta:
    pages = ceil(total / size) if size > 0 and total > 0 else (0 if total == 0 else 1)
    return ListMeta(total=total, page=page, pages=pages, size=size)
