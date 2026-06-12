#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete fix for all database models
"""

import os
from pathlib import Path

def check_project_model():
    """بررسی مدل Project"""
    print("=" * 70)
    print("🔍 بررسی api/models/project.py...")
    print("=" * 70)
    
    path = Path("api/models/project.py")
    if not path.exists():
        print("   ❌ فایل یافت نشد")
        return None
    
    content = path.read_text(encoding='utf-8')
    print(f"   ✅ فایل یافت شد ({len(content)} bytes)")
    
    # نمایش کلاس‌های موجود
    import re
    classes = re.findall(r'class\s+(\w+)\s*\(', content)
    if classes:
        print(f"   📋 کلاس‌های یافت شده: {', '.join(classes)}")
    
    return content


def check_iot_models():
    """بررسی مدل‌های IoT برای sensor_readings"""
    print("\n" + "=" * 70)
    print("🔍 بررسی api/modules/iot/models.py...")
    print("=" * 70)
    
    path = Path("api/modules/iot/models.py")
    if not path.exists():
        print("   ❌ فایل یافت نشد")
        return None
    
    content = path.read_text(encoding='utf-8')
    print(f"   ✅ فایل یافت شد ({len(content)} bytes)")
    
    # بررسی sensor_readings
    if 'sensor_readings' in content:
        print("   ✅ جدول sensor_readings تعریف شده")
    else:
        print("   ⚠️  جدول sensor_readings یافت نشد")
    
    # نمایش کلاس‌ها
    import re
    classes = re.findall(r'class\s+(\w+)\s*\(', content)
    if classes:
        print(f"   📋 کلاس‌های یافت شده: {', '.join(classes[:10])}")
    
    return content


def fix_all_models():
    """بازنویسی all_models.py با تمام مدل‌ها"""
    print("\n" + "=" * 70)
    print("🔧 بازنویسی api/modules/all_models.py...")
    print("=" * 70)
    
    content = '''"""
Import all models for database initialization
Complete version with all dependencies
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
    print(f"   ✅ فایل بازنویسی شد ({len(content)} bytes)")
    print("   ✅ Project اضافه شد")
    print("   ✅ iot_models اضافه شد")


def delete_database():
    """حذف دیتابیس قدیمی"""
    print("\n" + "=" * 70)
    print("🗑️ حذف دیتابیس قدیمی...")
    print("=" * 70)
    
    db_paths = [
        Path("econojin.db"),
        Path("api/econojin.db"),
    ]
    
    deleted = False
    for db_path in db_paths:
        if db_path.exists():
            try:
                db_path.unlink()
                print(f"   ✅ حذف شد: {db_path}")
                deleted = True
            except Exception as e:
                print(f"   ❌ خطا در حذف {db_path}: {e}")
    
    if not deleted:
        print("   ℹ️  دیتابیسی برای حذف وجود نداشت")


def main():
    print("\n" + "=" * 70)
    print("🚀 Econojin Complete Database Fix")
    print("=" * 70)
    print()
    
    try:
        # بررسی مدل‌ها
        check_project_model()
        check_iot_models()
        
        # اصلاح all_models
        fix_all_models()
        
        # حذف دیتابیس
        delete_database()
        
        # دستورالعمل‌ها
        print("\n" + "=" * 70)
        print("✅ تمام اصلاحات انجام شد!")
        print("=" * 70)
        print()
        print("📋 گام‌های بعدی:")
        print()
        print("1. سرور بک‌اند را ری‌استارت کنید:")
        print("   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        print()
        print("2. باید این خروجی را ببینید:")
        print("   ✅ Database initialized")
        print("   ✅ Early Warning Engine started")
        print()
        print("3. API را تست کنید:")
        print("   Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/soil-water/recent-analyses?limit=10' -UseBasicParsing")
        print()
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()