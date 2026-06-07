# api/core/schemas.py
"""
Standardized Pydantic Schemas for Econojin API
These models ensure consistent API responses across all modules.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SuccessResponse(BaseModel):
    """Standard response for successful operations (updates, deletes)."""
    success: bool = True
    message: str = "Operation completed successfully"

class IDResponse(BaseModel):
    """Standard response for resource creation."""
    id: int
    status: str = "created"

class StatsResponse(BaseModel):
    """Standard response for statistics and dashboards."""
    total: int = 0
    active: int = 0
    details: Dict[str, Any] = {}

class PaginatedResponse(BaseModel):
    """Standard response for paginated lists."""
    items: List[Any] = []
    total: int = 0
    limit: int = 50
    offset: int = 0

class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
