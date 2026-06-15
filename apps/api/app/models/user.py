"""User Model"""

from sqlalchemy import Column, String, Integer, Float, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base, TimestampMixin, IDMixin


class UserRole(str, enum.Enum):
    FARMER = "farmer"
    RESEARCHER = "researcher"
    INVESTOR = "investor"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"


class User(Base, IDMixin, TimestampMixin):
    """User model"""
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.FARMER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)
    trust_score = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)
    location = Column(String)
    bio = Column(String)

    # Relationships
    projects = relationship("Project", back_populates="manager")
    data_points = relationship("DataPoint", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    audits = relationship("Audit", back_populates="user")
