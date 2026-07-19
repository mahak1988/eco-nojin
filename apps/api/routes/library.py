"""
Library Router - Database backed
================================
RESTful endpoints for digital library and resource management.
"""

from typing import Optional
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.api.schemas.library import (
    LibraryResourceCreate, LibraryResourceUpdate,
    LibraryResourceResponse, LibraryResourceListResponse, LibraryStats,
    FileUploadResponse
)
from apps.api.services.library import LibraryService

router = APIRouter(prefix="/api/v1/library", tags=["📖 Library"])


@router.get("/", response_model=LibraryResourceListResponse)
async def list_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None, description="Search by title, description, or tags"),
    category: Optional[str] = Query(None, description="Filter by category"),
    author: Optional[str] = Query(None, description="Filter by author"),
    session: AsyncSession = Depends(get_db_session)
) -> LibraryResourceListResponse:
    """List library resources with optional search and filtering."""
    service = LibraryService(session)
    resources, total = await service.list(skip, limit, search, category, author)
    items = [LibraryResourceResponse.model_validate(r) for r in resources]
    return LibraryResourceListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/stats", response_model=LibraryStats)
async def get_stats(session: AsyncSession = Depends(get_db_session)) -> LibraryStats:
    """Get statistics about library resources."""
    service = LibraryService(session)
    stats = await service.get_stats()
    return LibraryStats(**stats)


@router.post("/", response_model=LibraryResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    payload: LibraryResourceCreate,
    session: AsyncSession = Depends(get_db_session)
) -> LibraryResourceResponse:
    """Create a new library resource."""
    service = LibraryService(session)
    resource = await service.create(payload)
    await session.commit()
    return LibraryResourceResponse.model_validate(resource)


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    title: str = Query(..., description="Resource title"),
    category: str = Query(..., description="Resource category"),
    session: AsyncSession = Depends(get_db_session)
) -> FileUploadResponse:
    """Upload a file and create a library resource entry."""
    # Read file content
    content = await file.read()
    file_size = len(content)

    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".bin"
    unique_filename = f"{uuid.uuid4()}{file_ext}"

    # Determine upload directory (create if needed)
    upload_dir = "uploads/library"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    # Create resource entry
    service = LibraryService(session)
    resource = await service.create(
        LibraryResourceCreate(
            title=title,
            category=category,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type
        )
    )
    await session.commit()

    return FileUploadResponse(
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type,
        resource_id=resource.id
    )


@router.get("/{resource_id}", response_model=LibraryResourceResponse)
async def get_resource(
    resource_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> LibraryResourceResponse:
    """Get a specific library resource by ID."""
    service = LibraryService(session)
    try:
        resource = await service.get(resource_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return LibraryResourceResponse.model_validate(resource)


@router.patch("/{resource_id}", response_model=LibraryResourceResponse)
async def update_resource(
    resource_id: int,
    payload: LibraryResourceUpdate,
    session: AsyncSession = Depends(get_db_session)
) -> LibraryResourceResponse:
    """Update an existing library resource."""
    service = LibraryService(session)
    try:
        resource = await service.update(resource_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return LibraryResourceResponse.model_validate(resource)


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> None:
    """Delete a library resource."""
    service = LibraryService(session)
    try:
        await service.delete(resource_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()


@router.post("/{resource_id}/download", response_model=LibraryResourceResponse)
async def download_resource(
    resource_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> LibraryResourceResponse:
    """Record a download for a resource."""
    service = LibraryService(session)
    try:
        resource = await service.download(resource_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return LibraryResourceResponse.model_validate(resource)