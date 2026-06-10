"""
Project Model
=============
مدل پروژه برای EconoJin
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.database import Base
import enum
from datetime import datetime


class ProjectStatus(str, enum.Enum):
    """وضعیت پروژه"""
    DRAFT = "draft"
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    """مدل پروژه"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # موقعیت جغرافیایی
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    area_ha = Column(Float, nullable=True, comment="مساحت به هکتار")
    
    # وضعیت
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # اطلاعات اضافی
    owner = Column(String(100), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    # parcel_polygons = relationship("GISParcelPolygon", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', code='{self.code}')>"
    
    def to_dict(self):
        """تبدیل به دیکشنری"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "area_ha": self.area_ha,
            "status": self.status.value if self.status else None,
            "is_active": self.is_active,
            "owner": self.owner,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
