"""
Econojin - Base CRUD Module
=============================
Adapted from fastapi/full-stack-fastapi-template with async SQLAlchemy support.
Provides reusable CRUD operations for all domain models.
"""

from typing import Any, Generic, TypeVar
from pydantic import BaseModel

from sqlalchemy import select, func, delete as sa_delete, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import Base

# Type variables for generic CRUD
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for CRUD operations on SQLAlchemy models.
    
    Provides standard create, read, update, delete, and list operations
    that can be inherited by domain-specific CRUD classes.
    
    Usage:
        class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
            pass
        
        crud_user = CRUDUser(User)
    """

    def __init__(self, model: type[ModelType]):
        """
        Initialize CRUD with the SQLAlchemy model class.
        
        Args:
            model: The SQLAlchemy model class (e.g., User)
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """
        Get a record by its primary key.
        
        Args:
            db: Database session
            id: Primary key value
            
        Returns:
            Model instance or None if not found
        """
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        order_by: Any | None = None,
    ) -> list[ModelType]:
        """
        Get multiple records with pagination and optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            filters: Optional dictionary of field:value filters
            order_by: Optional column to order by
            
        Returns:
            List of model instances
        """
        query = select(self.model)
        
        if filters:
            for field, value in filters.items():
                column = getattr(self.model, field, None)
                if column is not None:
                    query = query.where(column == value)
        
        if order_by is not None:
            query = query.order_by(order_by)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_count(
        self,
        db: AsyncSession,
        filters: dict[str, Any] | None = None,
    ) -> int:
        """
        Get total count of records, optionally filtered.
        
        Args:
            db: Database session
            filters: Optional dictionary of field:value filters
            
        Returns:
            Total count
        """
        query = select(func.count()).select_from(self.model)
        
        if filters:
            for field, value in filters.items():
                column = getattr(self.model, field, None)
                if column is not None:
                    query = query.where(column == value)
        
        result = await db.execute(query)
        return result.scalar_one()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Database session
            obj_in: Pydantic schema with creation data
            
        Returns:
            Created model instance
        """
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """
        Update an existing record.
        
        Args:
            db: Database session
            db_obj: Existing model instance to update
            obj_in: Pydantic schema or dict with update data
            
        Returns:
            Updated model instance
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> ModelType | None:
        """
        Delete a record by its primary key.
        
        Args:
            db: Database session
            id: Primary key value
            
        Returns:
            Deleted model instance or None if not found
        """
        obj = await self.get(db=db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def bulk_create(
        self, db: AsyncSession, *, objs_in: list[CreateSchemaType]
    ) -> list[ModelType]:
        """
        Create multiple records in a single transaction.
        
        Args:
            db: Database session
            objs_in: List of Pydantic schemas with creation data
            
        Returns:
            List of created model instances
        """
        db_objs = [self.model(**obj_in.model_dump(exclude_unset=True)) for obj_in in objs_in]
        db.add_all(db_objs)
        await db.commit()
        for obj in db_objs:
            await db.refresh(obj)
        return db_objs