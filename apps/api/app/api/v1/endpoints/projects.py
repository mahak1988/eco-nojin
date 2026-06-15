"""Projects Endpoints - Full CRUD"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
)
from app.services.project_service import (
    get_project_by_id, get_projects, create_project, update_project, delete_project,
)


router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project_endpoint(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(["admin", "researcher", "farmer"])),
):
    """Create a new project"""
    project = await create_project(db, project_data, current_user.id)
    return project


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    type: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """List all projects with filters and pagination"""
    skip = (page - 1) * per_page
    projects, total = await get_projects(
        db, skip=skip, limit=per_page,
        status=status, type=type, country=country, search=search,
    )
    return ProjectListResponse(
        projects=projects,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Get project by ID"""
    project = await get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project_endpoint(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Update project (admin or manager only)"""
    project = await get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    if current_user.role.value != "admin" and project.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this project",
        )
    
    return await update_project(db, project, project_data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_endpoint(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(["admin"])),
):
    """Delete project (admin only)"""
    project = await get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    await delete_project(db, project)
