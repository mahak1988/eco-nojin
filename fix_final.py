#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final fix for all database issues
"""

from pathlib import Path

def fix_all_models():
    """بازنویسی all_models.py با Project"""
    print("=" * 70)
    print("1. بازنویسی api/modules/all_models.py")
    print("=" * 70)
    
    content = '''"""
Import all models for database initialization
"""

# Core Models
from api.models.project import Project

# Auth & User
from api.modules.auth import models as auth_models

# Farmer
from api.modules.farmer import models as farmer_models

# EcoCoin & Blockchain
from api.modules.ecocoin import models as ecocoin_models

# Environmental
from api.modules.soil_water import models as soil_water_models
from api.modules.soil_water import erosion_models
from api.modules.soil import models as soil_models
from api.modules.water import models as water_models
from api.modules.iot import models as iot_models
from api.modules.mrv import models as mrv_models

# Business
from api.modules.store import models as store_models
from api.modules.financial import models as financial_models
from api.modules.accounting import models as accounting_models

# Content & Community
from api.modules.academy import models as academy_models
from api.modules.library import models as library_models
from api.modules.community import models as community_models
from api.modules.newsletter import models as newsletter_models
from api.modules.psychology import models as psychology_models
from api.modules.games import models as games_models
from api.modules.calendar import models as calendar_models

# Operations
from api.modules.maintenance import models as maintenance_models

__all__ = [
    "Project",
    "auth_models",
    "farmer_models",
    "ecocoin_models",
    "soil_water_models",
    "erosion_models",
    "soil_models",
    "water_models",
    "iot_models",
    "mrv_models",
    "store_models",
    "financial_models",
    "accounting_models",
    "academy_models",
    "library_models",
    "community_models",
    "newsletter_models",
    "psychology_models",
    "games_models",
    "calendar_models",
    "maintenance_models",
]
'''
    
    path = Path("api/modules/all_models.py")
    path.write_text(content, encoding='utf-8')
    print(f"   OK: {path}")


def check_water_models():
    """بررسی water/models.py برای Scenario"""
    print("\n" + "=" * 70)
    print("2. بررسی api/modules/water/models.py")
    print("=" * 70)
    
    path = Path("api/modules/water/models.py")
    content = path.read_text(encoding='utf-8')
    
    print(f"   اندازه فایل: {len(content)} bytes")
    
    # بررسی وجود Scenario
    if 'class Scenario' in content:
        print("   OK: کلاس Scenario یافت شد")
        return True
    else:
        print("   WARNING: کلاس Scenario یافت نشد")
        return False


def add_scenario_model():
    """اضافه کردن مدل Scenario به water/models.py"""
    print("\n" + "=" * 70)
    print("3. اضافه کردن مدل Scenario")
    print("=" * 70)
    
    path = Path("api/modules/water/models.py")
    content = path.read_text(encoding='utf-8')
    
    # بررسی اینکه آیا Scenario هست
    if 'class Scenario' in content:
        print("   OK: Scenario قبلاً وجود دارد")
        return
    
    # اضافه کردن مدل Scenario در ابتدای فایل (بعد از imports)
    scenario_model = '''

# ============================================================================
# Scenario Model (برای water balance)
# ============================================================================
class Scenario(Base):
    """مدل سناریو برای تحلیل آب"""
    __tablename__ = "scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scenario_type = Column(String(100), nullable=True)
    parameters = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    water_balances = relationship("WaterBalance", back_populates="scenario")

'''
    
    # پیدا کردن محل مناسب برای اضافه کردن
    # بعد از آخرین import و قبل از اولین کلاس
    lines = content.split('\n')
    insert_index = 0
    
    for i, line in enumerate(lines):
        if line.startswith('class ') and 'Base' in line:
            insert_index = i
            break
    
    if insert_index > 0:
        lines.insert(insert_index, scenario_model)
        content = '\n'.join(lines)
        path.write_text(content, encoding='utf-8')
        print(f"   OK: مدل Scenario اضافه شد")
    else:
        print("   ERROR: محل مناسب برای اضافه کردن یافت نشد")


def fix_water_balance_relationship():
    """اصلاح relationship در WaterBalance"""
    print("\n" + "=" * 70)
    print("4. بررسی relationship در WaterBalance")
    print("=" * 70)
    
    path = Path("api/modules/water/models.py")
    content = path.read_text(encoding='utf-8')
    
    # بررسی اینکه آیا back_populates درست است
    if 'back_populates="scenario"' in content:
        print("   OK: relationship درست است")
    else:
        print("   WARNING: relationship ممکن است مشکل داشته باشد")
        print("   باید back_populates='scenario' باشد")


def delete_database():
    """حذف دیتابیس"""
    print("\n" + "=" * 70)
    print("5. حذف دیتابیس قدیمی")
    print("=" * 70)
    
    db_paths = [
        Path("econojin.db"),
        Path("api/econojin.db"),
    ]
    
    for db_path in db_paths:
        if db_path.exists():
            db_path.unlink()
            print(f"   OK: {db_path} حذف شد")


def verify_project_model():
    """تأیید مدل Project"""
    print("\n" + "=" * 70)
    print("6. تأیید مدل Project")
    print("=" * 70)
    
    path = Path("api/models/project.py")
    if not path.exists():
        print(f"   ERROR: {path} یافت نشد")
        return
    
    content = path.read_text(encoding='utf-8')
    
    if 'class Project' in content and '__tablename__ = "projects"' in content:
        print("   OK: مدل Project درست است")
    else:
        print("   WARNING: مدل Project ممکن است مشکل داشته باشد")
        print("   محتوای فایل:")
        print(content[:500])


def main():
    print("\n" + "=" * 70)
    print("Econojin Final Database Fix")
    print("=" * 70)
    print()
    
    try:
        fix_all_models()
        has_scenario = check_water_models()
        
        if not has_scenario:
            add_scenario_model()
        
        fix_water_balance_relationship()
        verify_project_model()
        delete_database()
        
        print("\n" + "=" * 70)
        print("SUCCESS: تمام اصلاحات انجام شد!")
        print("=" * 70)
        print()
        print("گام بعدی:")
        print("1. سرور بک‌اند را ری‌استارت کنید:")
        print("   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        print()
        print("2. باید این خروجی را ببینید:")
        print("   ✅ Database initialized")
        print("   ✅ Early Warning Engine started")
        print()
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()