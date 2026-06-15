"""Project Service - Business Logic for Projects"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple

from app.models.project import Project, ProjectType, ProjectStatus
from app.models.data_point import DataPoint
from app.models.kpi import KPI
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


async def get_project_by_id(db: AsyncSession, project_id: int) -> Optional[Project]:
    """Get project by ID with manager"""
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.manager))
        .where(Project.id == project_id)
    )
    return result.scalar_one_or_none()


async def get_projects(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    type: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
) -> Tuple[List[Project], int]:
    """Get list of projects with filters"""
    query = select(Project).options(selectinload(Project.manager))
    count_query = select(func.count(Project.id))
    
    if status:
        query = query.where(Project.status == status)
        count_query = count_query.where(Project.status == status)
    if type:
        query = query.where(Project.type == type)
        count_query = count_query.where(Project.type == type)
    if country:
        query = query.where(Project.country == country)
        count_query = count_query.where(Project.country == country)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(Project.name.ilike(search_pattern))
        count_query = count_query.where(Project.name.ilike(search_pattern))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    query = query.offset(skip).limit(limit).order_by(Project.created_at.desc())
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return projects, total


async def create_project(
    db: AsyncSession,
    project_data: ProjectCreate,
    manager_id: int,
) -> Project:
    """Create a new project"""
    project = Project(
        name=project_data.name,
        description=project_data.description,
        country=project_data.country,
        region=project_data.region,
        type=ProjectType(project_data.type),
        status=ProjectStatus.PLANNING,
        hectares=project_data.hectares,
        budget=project_data.budget,
        spent=0.0,
        progress=0,
        manager_id=project_data.manager_id or manager_id,
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    # Reload with manager
    return await get_project_by_id(db, project.id)


async def update_project(
    db: AsyncSession,
    project: Project,
    project_data: ProjectUpdate,
) -> Project:
    """Update project"""
    update_data = project_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if key == "type":
            setattr(project, key, ProjectType(value))
        elif key == "status":
            setattr(project, key, ProjectStatus(value))
        else:
            setattr(project, key, value)
    
    await db.commit()
    await db.refresh(project)
    
    return await get_project_by_id(db, project.id)


async def delete_project(db: AsyncSession, project: Project) -> None:
    """Delete project with all related data (cascade)"""
    # Explicitly delete related data first
    await db.execute(
        delete(DataPoint).where(DataPoint.project_id == project.id)
    )
    await db.execute(
        delete(KPI).where(KPI.project_id == project.id)
    )
    
    # Now delete the project
    await db.delete(project)
    await db.commit()
