"""Base Model with common fields"""

from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class TimestampMixin:
    """Mixin for created_at and updated_at fields"""
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class IDMixin:
    """Mixin for ID field"""
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
