"""Shared Pydantic schemas."""

from apps.shared_core.schemas.errors import ErrorBody, ErrorResponse, error_dict
from apps.shared_core.schemas.pagination import (
    ListEnvelope,
    ListMeta,
    Page,
    PageMeta,
    build_meta,
    build_page,
    page_params,
    page_to_offset,
)

__all__ = [
    "ErrorBody",
    "ErrorResponse",
    "error_dict",
    "ListEnvelope",
    "ListMeta",
    "Page",
    "PageMeta",
    "build_meta",
    "build_page",
    "page_params",
    "page_to_offset",
]
