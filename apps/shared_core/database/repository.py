from typing import TypeVar, Generic, Type, Any, Dict, List, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """
    پیاده‌سازی Generic الگوی Repository برای SQLAlchemy 2.0 Async.
    
    استفاده:
        class UserRepository(BaseRepository[User]):
            def __init__(self, session: AsyncSession):
                super().__init__(session, User)
    """
    
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: Any, options: Optional[Sequence[Any]] = None) -> Optional[T]:
        """دریافت رکورد بر اساس شناسه اصلی."""
        try:
            stmt = select(self.model).where(self.model.id == id)
            if options:
                stmt = stmt.options(*options)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching {self.model.__name__} by id {id}: {e}")
            raise

    async def get_multi(
        self,
        filter_by: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
        options: Optional[Sequence[Any]] = None
    ) -> List[T]:
        """دریافت چندین رکورد با فیلتر و صفحه‌بندی."""
        try:
            stmt = select(self.model)
            if filter_by:
                for key, value in filter_by.items():
                    stmt = stmt.where(getattr(self.model, key) == value)
            if options:
                stmt = stmt.options(*options)
            
            stmt = stmt.limit(limit).offset(offset)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error fetching multiple {self.model.__name__}: {e}")
            raise

    async def create(self, obj_in: Dict[str, Any]) -> T:
        """ایجاد رکورد جدید."""
        try:
            db_obj = self.model(**obj_in)
            self.session.add(db_obj)
            await self.session.flush()
            await self.session.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise

    async def update(self, db_obj: T, obj_in: Dict[str, Any]) -> T:
        """بروزرسانی رکورد موجود."""
        try:
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            await self.session.flush()
            await self.session.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model.__name__}: {e}")
            raise

    async def delete(self, id: Any) -> bool:
        """حذف رکورد بر اساس شناسه."""
        try:
            stmt = delete(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            await self.session.flush()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Error deleting {self.model.__name__} with id {id}: {e}")
            raise

    async def count(self, filter_by: Optional[Dict[str, Any]] = None) -> int:
        """شمارش تعداد رکوردها - بهینه‌سازی شده با استفاده از count(*)"""
        try:
            # بهینه‌سازی: استفاده مستقیم از func.count() بدون load کردن داده‌ها
            stmt = select(func.count(1)).select_from(self.model)
            if filter_by:
                for key, value in filter_by.items():
                    stmt = stmt.where(getattr(self.model, key) == value)
            result = await self.session.execute(stmt)
            return result.scalar_one() or 0
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            raise

    async def count_fast(self, filter_by: Optional[Dict[str, Any]] = None) -> int:
        """
        شمارش سریع - برای دیتابیس‌های بزرگ
        نکته: در PostgreSQL می‌توان از estimate استفاده کرد
        """
        try:
            stmt = select(func.count(1)).select_from(self.model)
            if filter_by:
                for key, value in filter_by.items():
                    stmt = stmt.where(getattr(self.model, key) == value)
            result = await self.session.execute(stmt)
            return result.scalar_one() or 0
        except SQLAlchemyError as e:
            logger.error(f"Error fast counting {self.model.__name__}: {e}")
            raise