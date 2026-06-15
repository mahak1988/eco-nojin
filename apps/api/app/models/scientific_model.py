"""
ScientificModel Database Model
Stores metadata and configuration for all 40 scientific models.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.models.base import Base


class ScientificModel(Base):
    """Scientific model metadata and configuration"""
    __tablename__ = "scientific_models"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    
    # Description and documentation
    description = Column(Text, nullable=True)
    formula = Column(String(500), nullable=True)
    interpretation_guide = Column(Text, nullable=True)
    standards = Column(Text, nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    default_parameters = Column(JSON, nullable=True)
    
    # Usage statistics
    usage_count = Column(Integer, default=0, nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ScientificModel(model_id='{self.model_id}', name='{self.name}')>"
