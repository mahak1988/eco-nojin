#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug and fix database issues
"""

import os
import sys
from pathlib import Path

def check_database_exists():
    """بررسی وجود دیتابیس"""
    print("=" * 70)
    print("🔍 بررسی دیتابیس...")
    print("=" * 70)
    
    db_paths = [
        Path("econojin.db"),
        Path("api/econojin.db"),
    ]
    
    found = False
    for db_path in db_paths:
        if db_path.exists():
            size = db_path.stat().st_size
            print(f"   ⚠️  یافت شد: {db_path} ({size} bytes)")
            found = True
    
    if not found:
        print("   ✅ دیتابیس وجود ندارد")
    
    return found


def delete_database():
    """حذف دیتابیس"""
    print("\n" + "=" * 70)
    print("🗑️ حذف دیتابیس...")
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
    
    return deleted


def check_models():
    """بررسی مدل‌ها"""
    print("\n" + "=" * 70)
    print("📋 بررسی مدل‌های مهم...")
    print("=" * 70)
    
    models_to_check = [
        ("api/modules/soil_water/models.py", "SoilWaterAnalysis", ["field_name", "soil_texture", "bulk_density"]),
        ("api/modules/farmer/models.py", "Farmer", ["soil_erosion_analyses"]),
    ]
    
    for model_file, class_name, columns in models_to_check:
        path = Path(model_file)
        if not path.exists():
            print(f"   ❌ فایل یافت نشد: {model_file}")
            continue
        
        content = path.read_text(encoding='utf-8')
        
        print(f"\n   📄 {model_file}")
        print(f"      Class: {class_name}")
        
        # بررسی وجود کلاس
        if f"class {class_name}" in content:
            print(f"      ✅ کلاس یافت شد")
        else:
            print(f"      ❌ کلاس یافت نشد")
            continue
        
        # بررسی ستون‌ها
        for column in columns:
            if column in content:
                print(f"      ✅ ستون {column} وجود دارد")
            else:
                print(f"      ❌ ستون {column} وجود ندارد")


def check_imports():
    """بررسی import ها در all_models"""
    print("\n" + "=" * 70)
    print("📦 بررسی all_models.py...")
    print("=" * 70)
    
    path = Path("api/modules/all_models.py")
    if not path.exists():
        print("   ❌ فایل یافت نشد")
        return
    
    content = path.read_text(encoding='utf-8')
    
    # بررسی import های مشکل‌دار
    problematic_imports = [
        "api.modules.users",
        "api.modules.projects",
    ]
    
    for imp in problematic_imports:
        if imp in content:
            print(f"   ❌ import مشکل‌دار: {imp}")
        else:
            print(f"   ✅ {imp} حذف شده")
    
    # شمارش import ها
    import_count = content.count("from api.modules")
    print(f"\n   📊 تعداد import ها: {import_count}")


def main():
    print("\n" + "=" * 70)
    print("🚀 Econojin Debug & Fix Script")
    print("=" * 70)
    print()
    
    # بررسی دیتابیس
    db_exists = check_database_exists()
    
    # حذف دیتابیس
    if db_exists:
        delete_database()
    
    # بررسی مدل‌ها
    check_models()
    
    # بررسی import ها
    check_imports()
    
    # دستورالعمل‌ها
    print("\n" + "=" * 70)
    print("📋 دستورالعمل‌های بعدی:")
    print("=" * 70)
    print()
    print("1. سرور بک‌اند را ری‌استارت کنید:")
    print("   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
    print()
    print("2. در یک ترمینال جدید، API را تست کنید:")
    print("   Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/soil-water/recent-analyses?limit=10' -UseBasicParsing")
    print()
    print("3. اگر باز هم خطا دیدید، لاگ سرور را بررسی کنید")
    print()
    print("4. یا Swagger UI را باز کنید:")
    print("   http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()