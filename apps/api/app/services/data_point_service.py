"""DataPoint Service - Business Logic for Data Points"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List, Tuple

from app.models.data_point import DataPoint, DataStatus
from app.schemas.data_point import DataPointCreate, DataPointUpdate


async def get_data_point_by_id(db: AsyncSession, data_point_id: int) -> Optional[DataPoint]:
    """Get data point by ID"""
    result = await db.execute(
        select(DataPoint).where(DataPoint.id == data_point_id)
    )
    return result.scalar_one_or_none()


async def get_data_points(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    module_id: Optional[int] = None,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
) -> Tuple[List[DataPoint], int]:
    """Get list of data points with filters"""
    query = select(DataPoint)
    count_query = select(func.count(DataPoint.id))
    
    if project_id:
        query = query.where(DataPoint.project_id == project_id)
        count_query = count_query.where(DataPoint.project_id == project_id)
    if module_id:
        query = query.where(DataPoint.module_id == module_id)
        count_query = count_query.where(DataPoint.module_id == module_id)
    if user_id:
        query = query.where(DataPoint.user_id == user_id)
        count_query = count_query.where(DataPoint.user_id == user_id)
    if status:
        query = query.where(DataPoint.status == status)
        count_query = count_query.where(DataPoint.status == status)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    query = query.offset(skip).limit(limit).order_by(DataPoint.timestamp.desc())
    result = await db.execute(query)
    data_points = result.scalars().all()
    
    return data_points, total


async def create_data_point(
    db: AsyncSession,
    data_point_data: DataPointCreate,
    user_id: int,
) -> DataPoint:
    """Create a new data point"""
    data_point = DataPoint(
        project_id=data_point_data.project_id,
        module_id=data_point_data.module_id,
        user_id=user_id,
        data_type=data_point_data.data_type,
        value=data_point_data.value,
        unit=data_point_data.unit,
        timestamp=data_point_data.timestamp,
        status=DataStatus.PENDING,
        extra_data=data_point_data.extra_data or {},
    )
    
    db.add(data_point)
    await db.commit()
    await db.refresh(data_point)
    return data_point


async def update_data_point(
    db: AsyncSession,
    data_point: DataPoint,
    data_point_data: DataPointUpdate,
) -> DataPoint:
    """Update data point"""
    update_data = data_point_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if key == "status":
            setattr(data_point, key, DataStatus(value))
        else:
            setattr(data_point, key, value)
    
    await db.commit()
    await db.refresh(data_point)
    return data_point


async def delete_data_point(db: AsyncSession, data_point: DataPoint) -> None:
    """Delete data point"""
    await db.delete(data_point)
    await db.commit()
