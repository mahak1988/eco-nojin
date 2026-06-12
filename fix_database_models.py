#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix all database model issues for Econojin
"""

def fix_all_models():
    """بازنویسی all_models.py با فقط ماژول‌های موجود"""
    print("=" * 70)
    print("1. بازنویسی api/modules/all_models.py")
    print("=" * 70)
    
    content = '''"""
Import all models for database initialization
Only import existing modules
"""

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
    
    path = r"api\modules\all_models.py"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"   OK: {path}")
    print(f"   Size: {len(content)} bytes")


def fix_farmer_model():
    """اصلاح مدل Farmer برای اضافه کردن رابطه soil_erosion_analyses"""
    print("\n" + "=" * 70)
    print("2. اصلاح api/modules/farmer/models.py")
    print("=" * 70)
    
    path = r"api\modules\farmer\models.py"
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. مطمئن شویم relationship import شده
    if 'from sqlalchemy.orm import' not in content:
        # اضافه کردن import در ابتدای فایل
        content = 'from sqlalchemy.orm import relationship\n' + content
        print("   + Added: from sqlalchemy.orm import relationship")
    elif 'relationship' not in content.split('from sqlalchemy.orm import')[1].split('\n')[0]:
        # اضافه کردن relationship به import موجود
        content = content.replace(
            'from sqlalchemy.orm import',
            'from sqlalchemy.orm import relationship,'
        )
        print("   + Added: relationship to existing import")
    
    # 2. اضافه کردن رابطه soil_erosion_analyses به کلاس Farmer
    if 'soil_erosion_analyses' not in content:
        # پیدا کردن انتهای کلاس Farmer
        lines = content.split('\n')
        farmer_class_start = -1
        farmer_class_end = -1
        
        for i, line in enumerate(lines):
            if 'class Farmer(Base):' in line or 'class Farmer(' in line:
                farmer_class_start = i
                # پیدا کردن انتهای کلاس
                for j in range(i + 1, len(lines)):
                    # اگر خط بعدی کلاس دیگری است یا فایل تمام شده
                    if lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                        farmer_class_end = j
                        break
                    if j == len(lines) - 1:
                        farmer_class_end = j + 1
                break
        
        if farmer_class_end > 0:
            # اضافه کردن رابطه قبل از انتهای کلاس
            relationship_line = '    soil_erosion_analyses = relationship("SoilErosionAnalysis", back_populates="farmer", lazy="selectin")'
            lines.insert(farmer_class_end, relationship_line)
            content = '\n'.join(lines)
            print("   + Added: soil_erosion_analyses relationship")
        else:
            print("   WARNING: Could not find Farmer class end")
    else:
        print("   OK: soil_erosion_analyses already exists")
    
    # نوشتن فایل
    if content != original_content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   OK: {path} updated")
    else:
        print(f"   OK: {path} unchanged")


def fix_erosion_models():
    """اطمینان از اینکه erosion_models.py درست import شده"""
    print("\n" + "=" * 70)
    print("3. بررسی api/modules/soil_water/erosion_models.py")
    print("=" * 70)
    
    path = r"api\modules\soil_water\erosion_models.py"
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # مطمئن شویم relationship import شده
    if 'from sqlalchemy.orm import' not in content:
        content = 'from sqlalchemy.orm import relationship\n' + content
        print("   + Added: from sqlalchemy.orm import relationship")
    
    # نوشتن فایل
    if content != original_content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   OK: {path} updated")
    else:
        print(f"   OK: {path} unchanged")


def verify_fixes():
    """تأیید اصلاحات"""
    print("\n" + "=" * 70)
    print("4. تأیید اصلاحات")
    print("=" * 70)
    
    # بررسی all_models.py
    with open(r"api\modules\all_models.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'api.modules.users' in content:
        print("   ERROR: api.modules.users still in all_models.py")
    else:
        print("   OK: api.modules.users removed")
    
    if 'api.modules.projects' in content:
        print("   ERROR: api.modules.projects still in all_models.py")
    else:
        print("   OK: api.modules.projects removed")
    
    # بررسی farmer/models.py
    with open(r"api\modules\farmer\models.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'soil_erosion_analyses' in content:
        print("   OK: soil_erosion_analyses relationship added to Farmer")
    else:
        print("   ERROR: soil_erosion_analyses not found in Farmer model")


def main():
    print("\n" + "=" * 70)
    print("Econojin Database Models Fix")
    print("=" * 70)
    print()
    
    try:
        fix_all_models()
        fix_farmer_model()
        fix_erosion_models()
        verify_fixes()
        
        print("\n" + "=" * 70)
        print("SUCCESS: All fixes applied!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Restart backend server:")
        print("   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        print()
        print("2. Expected output:")
        print("   - Database initialized")
        print("   - Early Warning Engine started")
        print("   - Ready on http://127.0.0.1:8000")
        print()
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()