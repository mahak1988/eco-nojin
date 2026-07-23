"""
api router | روتر api
=================================
FastAPI router exposing api endpoints.

Endpoints:
    GET    /api          List with pagination
    GET    /api/{id}    Get by ID
    POST   /api          Create
    PATCH  /api/{id}    Update
    DELETE /api/{id}    Delete
"""

from typing import Annotated
import logging
import time
from functools import wraps

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Adjust this import to match your project's database session dependency
try:
    from apps.shared_core.database.session import get_db_session
except ImportError:
    # Fallback stub — replace with real implementation
    from typing import AsyncGenerator
    async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
        raise NotImplementedError("Wire up get_db_session in apps.shared_core.database.session")

# Import caching module
try:
    from apps.shared_core.caching import cached, cache_manager
    CACHING_AVAILABLE = True
except ImportError:
    CACHING_AVAILABLE = False
    cached = lambda **kwargs: lambda f: f  # No-op decorator if caching not available

from apps.api.schemas import (
    ApiCreate,
    ApiUpdate,
    ApiResponse,
    ApiListResponse,
)
from apps.api.service import ApiService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["api"])


# Middleware for performance logging
def log_performance(func):
    """Decorator برای لاگ کردن زمان اجرای endpointها"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            if elapsed > 1.0:  # لاگ برای کوئری‌های کند (> 1 ثانیه)
                logger.warning(f"Slow query detected: {func.__name__} took {elapsed:.3f}s")
            elif elapsed > 0.5:
                logger.info(f"Query time: {func.__name__} took {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Error in {func.__name__} after {elapsed:.3f}s: {e}")
            raise
    return wrapper


@router.get("", response_model=ApiListResponse)
@log_performance
@cached(key_prefix="api_list", ttl=300)  # کش برای 5 دقیقه
async def list_api(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
):
    """List api records with pagination."""
    service = ApiService(session)
    items, total = await service.list(skip=skip, limit=limit)
    return ApiListResponse(
        items=[ApiResponse.model_validate(item) for item in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/{item_id}", response_model=ApiResponse)
@log_performance
@cached(key_prefix="api_detail", ttl=600)  # کش برای 10 دقیقه
async def get_api(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get a single api by ID."""
    service = ApiService(session)
    try:
        item = await service.get(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return ApiResponse.model_validate(item)


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
@log_performance
async def create_api(
    payload: ApiCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new api."""
    service = ApiService(session)
    item = await service.create(payload)
    await session.commit()
    
    # Invalidate cache after create
    if CACHING_AVAILABLE:
        await cache_manager.invalidate_pattern("api_*")
    
    return ApiResponse.model_validate(item)


@router.patch("/{item_id}", response_model=ApiResponse)
@log_performance
async def update_api(
    item_id: int,
    payload: ApiUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """Update an existing api."""
    service = ApiService(session)
    try:
        item = await service.update(item_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    
    # Invalidate cache after update
    if CACHING_AVAILABLE:
        await cache_manager.invalidate_pattern("api_*")
    
    return ApiResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
@log_performance
async def delete_api(
    item_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Delete a api by ID."""
    service = ApiService(session)
    try:
        await service.delete(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    
    # Invalidate cache after delete
    if CACHING_AVAILABLE:
        await cache_manager.invalidate_pattern("api_*")
    
    return None
