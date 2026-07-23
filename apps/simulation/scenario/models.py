"""
مدل‌های دیتابیس سناریو و مقایسه
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Float, DateTime, ForeignKey, JSON, Text, Boolean, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from apps.shared_core.database.base import Base


class Scenario(Base):
    """سناریوی شبیه‌سازی"""
    __tablename__ = "scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    simulator_id = Column(String(100), nullable=False, index=True)
    base_params = Column(JSON, nullable=False, default=dict)
    scenario_params = Column(JSON, nullable=False, default=dict)
    category = Column(String(100), nullable=True)  # irrigation, climate, soil, management
    is_preset = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    results = relationship("ScenarioResult", back_populates="scenario", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Scenario {self.name} ({self.simulator_id})>"


class ScenarioResult(Base):
    """نتیجهٔ اجرای سناریو"""
    __tablename__ = "scenario_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenarios.id"), nullable=False)
    metrics = Column(JSON, nullable=False, default=dict)
    outputs = Column(JSON, nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    status = Column(String(50), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

    scenario = relationship("Scenario", back_populates="results")


class ComparisonSession(Base):
    """جلسهٔ مقایسهٔ سناریوها"""
    __tablename__ = "comparison_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    scenario_ids = Column(JSON, nullable=False, default=list)  # لیست UUID سناریوها
    comparison_type = Column(String(100), default="side_by_side")  # side_by_side, overlay, table
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ComparisonSession {self.name} ({len(self.scenario_ids)} scenarios)>"


class ModelChain(Base):
    """زنجیرهٔ مدل‌ها"""
    __tablename__ = "model_chains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    chain_config = Column(JSON, nullable=False, default=dict)
    # chain_config نمونه:
    # {
    #   "steps": [
    #     {"simulator_id": "climate", "params": {...}, "output_mapping": {"temp_change": "temp_input"}},
    #     {"simulator_id": "aquacrop", "params": {...}, "input_from": "climate"},
    #     {"simulator_id": "cba", "params": {...}, "input_from": "aquacrop"}
    #   ]
    # }
    last_result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ═══════════════════════════════════════════════════════════
# سناریوهای پیش‌فرض (Preset Scenarios)
# ═══════════════════════════════════════════════════════════

PRESET_SCENARIOS = {
    "aquacrop": [
        {
            "id": "drip_irrigation",
            "name": "آبیاری قطره‌ای",
            "name_en": "Drip Irrigation",
            "description": "کاهش ۳۰٪ مصرف آب با سیستم قطره‌ای",
            "category": "irrigation",
            "params": {
                "total_irrigation": 175,  # 250 * 0.7
                "irrigation_efficiency": 0.95,
            },
        },
        {
            "id": "deficit_irrigation",
            "name": "آبیاری کم‌آبی",
            "name_en": "Deficit Irrigation",
            "description": "اعمال ۵۰٪ آبیاری در مرحلهٔ گلدهی",
            "category": "irrigation",
            "params": {
                "total_irrigation": 125,
                "deficit_stage": "flowering",
                "deficit_factor": 0.5,
            },
        },
        {
            "id": "climate_change_rcp45",
            "name": "تغییر اقلیم RCP4.5",
            "name_en": "Climate Change RCP4.5",
            "description": "افزایش ۱.۵ درجه دما و کاهش ۱۰٪ بارندگی",
            "category": "climate",
            "params": {
                "temp_offset": 1.5,
                "precip_factor": 0.9,
                "co2_ppm": 550,
            },
        },
        {
            "id": "climate_change_rcp85",
            "name": "تغییر اقلیم RCP8.5",
            "name_en": "Climate Change RCP8.5",
            "description": "افزایش ۴ درجه دما و کاهش ۲۵٪ بارندگی",
            "category": "climate",
            "params": {
                "temp_offset": 4.0,
                "precip_factor": 0.75,
                "co2_ppm": 900,
            },
        },
        {
            "id": "soil_amendment",
            "name": "اصلاح خاک",
            "name_en": "Soil Amendment",
            "description": "افزایش مادهٔ آلی خاک به ۳٪",
            "category": "soil",
            "params": {
                "field_capacity": 35,
                "wilting_point": 16,
                "organic_matter": 3.0,
            },
        },
        {
            "id": "early_planting",
            "name": "کاشت زودهنگام",
            "name_en": "Early Planting",
            "description": "کاشت ۲ هفته زودتر از تاریخ معمول",
            "category": "management",
            "params": {
                "planting_date": "2024-03-01",
                "planting_offset_days": -14,
            },
        },
        {
            "id": "drought_resistant",
            "name": "رقم مقاوم به خشکی",
            "name_en": "Drought Resistant Variety",
            "description": "استفاده از رقم مقاوم با نیاز آبی کمتر",
            "category": "management",
            "params": {
                "total_irrigation": 150,
                "drought_tolerance": 0.8,
                "root_depth_factor": 1.3,
            },
        },
    ],
    "dssat": [
        {
            "id": "nitrogen_optimization",
            "name": "بهینه‌سازی نیتروژن",
            "name_en": "Nitrogen Optimization",
            "description": "تنظیم مقدار و زمان مصرف نیتروژن",
            "category": "management",
            "params": {
                "n_rate": 180,
                "n_splits": 3,
                "n_timing": "optimized",
            },
        },
        {
            "id": "climate_adaptation",
            "name": "سازگاری اقلیمی",
            "name_en": "Climate Adaptation",
            "description": "تنظیم تاریخ کاشت و رقم بر اساس اقلیم آینده",
            "category": "climate",
            "params": {
                "planting_offset_days": -10,
                "cultivar": "heat_tolerant",
            },
        },
    ],
    "swat": [
        {
            "id": "buffer_strip",
            "name": "نوار حائل",
            "name_en": "Buffer Strip",
            "description": "ایجاد نوار حائل ۱۰ متری در حاشیهٔ رودخانه",
            "category": "management",
            "params": {
                "buffer_width": 10,
                "buffer_efficiency": 0.7,
            },
        },
        {
            "id": "cover_crop",
            "name": "گیاه پوششی",
            "name_en": "Cover Crop",
            "description": "کاشت گیاه پوششی در فصل غیرکشت",
            "category": "soil",
            "params": {
                "cover_crop": True,
                "cover_crop_type": "clover",
                "erosion_reduction": 0.4,
            },
        },
    ],
}
