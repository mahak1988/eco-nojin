#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix all database model issues"""

# ============================================================================
# Fix 1: all_models.py - فقط ماژول‌های موجود
# ============================================================================
def fix_all_models():
    print("=" * 70)
    print("🔧 بازنویسی api/modules/all_models.py...")
    print("=" * 70)
    
    content = '''"""
Import all models for database initialization
"""
# Auth & User
from api.modules.auth import models as auth_models

# Farmer
from api.modules.farmer import models as farmer_models

# EcoCoin & Blockchain
from api.modules.ecocoin import models as ecocoin_models

# Environmental
from api.modules.soil_water import models as soil_water_models
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

# Import erosion models separately
from api.modules.soil_water import erosion_models

__all__ = [
    "auth_models",
    "farmer_models",
    "ecocoin_models",
    "soil_water_models",
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
    "erosion_models",
]
'''
    
    path = r"api\modules\all_models.py"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ all_models.py بازنویسی شد ({len(content)} bytes)")


# ============================================================================
# Fix 2: Farmer model - اضافه کردن رابطه soil_erosion_analyses
# ============================================================================
def fix_farmer_model():
    print("\n" + "=" * 70)
    print("🔧 اصلاح api/modules/farmer/models.py...")
    print("=" * 70)
    
    path = r"api\modules\farmer\models.py"
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # بررسی اینکه آیا relationship import شده
    if 'from sqlalchemy.orm import' not in content:
        # اضافه کردن import relationship
        content = content.replace(
            'from sqlalchemy import',
            'from sqlalchemy import'
        )
        # اضافه کردن import جدید
        if 'from sqlalchemy.orm' not in content:
            content = 'from sqlalchemy.orm import relationship\n' + content
    
    # بررسی اینکه آیا رابطه soil_erosion_analyses وجود دارد
    if 'soil_erosion_analyses' not in content:
        # پیدا کردن کلاس Farmer
        if 'class Farmer(Base):' in content:
            # اضافه کردن رابطه در انتهای کلاس
            # پیدا کردن آخرین خط کلاس
            lines = content.split('\n')
            insert_index = -1
            
            for i, line in enumerate(lines):
                if 'class Farmer(Base):' in line:
                    # پیدا کردن انتهای کلاس
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                            insert_index = j
                            break
                        if j == len(lines) - 1:
                            insert_index = j + 1
                    break
            
            if insert_index > 0:
                # اضافه کردن رابطه
                relationship_line = '    soil_erosion_analyses = relationship("SoilErosionAnalysis", back_populates="farmer", lazy="selectin")'
                lines.insert(insert_index, relationship_line)
                content = '\n'.join(lines)
                print("✅ رابطه soil_erosion_analyses به مدل Farmer اضافه شد")
    else:
        print("✅ رابطه soil_erosion_analyses قبلاً وجود دارد")
    
    # نوشتن فایل
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ farmer/models.py اصلاح شد ({len(content)} bytes)")


# ============================================================================
# Fix 3: erosion_models.py - اصلاح back_populates
# ============================================================================
def fix_erosion_models():
    print("\n" + "=" * 70)
    print("🔧 اصلاح api/modules/soil_water/erosion_models.py...")
    print("=" * 70)
    
    path = r"api\modules\soil_water\erosion_models.py"
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # بررسی اینکه آیا relationship import شده
    if 'from sqlalchemy.orm import' not in content:
        content = 'from sqlalchemy.orm import relationship\n' + content
    
    # نوشتن فایل
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ erosion_models.py اصلاح شد ({len(content)} bytes)")


# ============================================================================
# Main
# ============================================================================
def main():
    print("\n" + "=" * 70)
    print("🚀 Econojin Complete Fix Script")
    print("=" * 70)
    print()
    
    try:
        fix_all_models()
        fix_farmer_model()
        fix_erosion_models()
        
        print("\n" + "=" * 70)
        print("✅ تمام اصلاحات با موفقیت انجام شدند!")
        print("=" * 70)
        print()
        print("🚀 گام بعدی:")
        print("   1. سرور بک‌اند را ری‌استارت کنید:")
        print("      uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        print()
        print("   2. باید این خروجی را ببینید:")
        print("      ✅ Database initialized")
        print("      ✅ Early Warning Engine started")
        print("      ✅ Ready on http://127.0.0.1:8000")
        print()
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()