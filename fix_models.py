#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix all_models.py and Farmer model issues"""

import re

# ============================================================================
# Fix 1: all_models.py - تغییر users به auth
# ============================================================================
def fix_all_models():
    print("=" * 70)
    print("🔧 اصلاح api/modules/all_models.py...")
    print("=" * 70)
    
    path = r"api\modules\all_models.py"
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 محتوای فعلی ({len(content)} bytes):")
        print("-" * 70)
        print(content[:500])
        print("...")
        print("-" * 70)
        
        # جایگزینی users با auth
        new_content = content.replace(
            'from api.modules.users import models as user_models',
            'from api.modules.auth import models as user_models'
        )
        
        # اگر خط دیگری هم وجود دارد
        new_content = new_content.replace(
            'api.modules.users',
            'api.modules.auth'
        )
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ فایل اصلاح شد ({len(new_content)} bytes)")
        
        # نمایش تغییرات
        if content != new_content:
            print("✅ تغییرات اعمال شد:")
            for line in new_content.split('\n'):
                if 'auth' in line.lower() and 'import' in line.lower():
                    print(f"   {line}")
        else:
            print("⚠️  هیچ تغییری اعمال نشد - فایل ممکن است قبلاً اصلاح شده باشد")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False


# ============================================================================
# Fix 2: Farmer model - بررسی و اصلاح soil_erosion_analyses
# ============================================================================
def fix_farmer_model():
    print("\n" + "=" * 70)
    print("🔧 بررسی api/modules/farmer/models.py...")
    print("=" * 70)
    
    path = r"api\modules\farmer\models.py"
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 اندازه فایل: {len(content)} bytes")
        
        # بررسی وجود soil_erosion_analyses
        if 'soil_erosion_analyses' in content:
            print("✅ رابطه soil_erosion_analyses در فایل وجود دارد")
            
            # بررسی اینکه آیا import شده یا نه
            if 'relationship' in content:
                print("✅ relationship import شده است")
            else:
                print("⚠️  relationship import نشده - اضافه می‌کنیم...")
                # اضافه کردن import relationship
                if 'from sqlalchemy.orm import' in content:
                    new_content = re.sub(
                        r'from sqlalchemy\.orm import ([^\n]+)',
                        lambda m: f"from sqlalchemy.orm import {m.group(1)}, relationship" if 'relationship' not in m.group(1) else m.group(0),
                        content
                    )
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print("✅ relationship به import اضافه شد")
        else:
            print("⚠️  رابطه soil_erosion_analyses در مدل Farmer وجود ندارد")
            print("   این ممکن است باعث خطا در EWS شود")
            print("   اما فعلاً سرور باید کار کند")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False


# ============================================================================
# Fix 3: بررسی database.py
# ============================================================================
def check_database():
    print("\n" + "=" * 70)
    print("🔍 بررسی api/core/database.py...")
    print("=" * 70)
    
    path = r"api\core\database.py"
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # بررسی init_db
        if 'from api.modules import all_models' in content:
            print("✅ database.py از all_models استفاده می‌کند")
        else:
            print("⚠️  database.py از all_models استفاده نمی‌کند")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False


# ============================================================================
# Main
# ============================================================================
def main():
    print("\n" + "=" * 70)
    print("🚀 Econojin Models Fix Script")
    print("=" * 70)
    print()
    
    success = True
    
    # Fix 1
    if not fix_all_models():
        success = False
    
    # Fix 2
    if not fix_farmer_model():
        success = False
    
    # Fix 3
    if not check_database():
        success = False
    
    print("\n" + "=" * 70)
    if success:
        print("✅ تمام اصلاحات با موفقیت انجام شدند!")
    else:
        print("⚠️  برخی اصلاحات با خطا مواجه شدند")
    print("=" * 70)
    print()
    print("🚀 گام بعدی:")
    print("   1. سرور بک‌اند را ری‌استارت کنید:")
    print("      uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
    print()
    print("   2. اگر خطای soil_erosion_analyses باقی ماند، باید:")
    print("      - یا رابطه را به مدل Farmer اضافه کنیم")
    print("      - یا Early Warning Engine را موقتاً غیرفعال کنیم")
    print()


if __name__ == "__main__":
    main()