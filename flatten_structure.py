#!/usr/bin/env python3
"""
اسکریپت یکپارچه‌سازی ساختار پروژه
حذف لایه‌های تودرتوی تکراری و یکپارچه‌سازی ساختار
"""

import os
import shutil
from pathlib import Path
from pathlib import Path

def flatten_nested_structure():
    """یکپارچه‌سازی ساختار تودرتو"""
    base_path = Path("apps/app")
    
    if not base_path.exists():
        print("❌ مسیر apps/app وجود ندارد")
        return
    
    # پیدا کردن تمام لایه‌های تودرتو
    nested_levels = []
    current = base_path
    
    # پیدا کردن لایه‌های تودرتو
    while True:
        next_level = current / "app"
        if next_level.exists() and next_level.is_dir():
            nested_levels.append(next_level)
            current = next_level
        else:
            break
    
    if not nested_levels:
        print("✅ هیچ لایه تودرتویی یافت نشد")
        return
    
    print(f"🔍 {len(nested_levels)} لایه تودرتو یافت شد")
    
    # ادغام لایه‌ها از عمیق‌ترین به سطحی‌ترین
    for i, nested_path in enumerate(reversed(nested_levels), 1):
        print(f"\n📦 لایه {i}: {nested_path}")
        
        # انتقال فایل‌ها به لایه بالاتر
        parent = nested_path.parent
        
        for item in nested_path.iterdir():
            target = parent / item.name
            
            if target.exists():
                print(f"  ⚠️  {item.name} از قبل وجود دارد - حذف تکراری")
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    path.unlink()
            else:
                print(f"  ➡️  انتقال {item.name} به {parent.name}")
                shutil.move(str(item), str(target))
        
        # حذف دایرکتوری خالی
        if nested_path.exists() and not any(nested_path.iterdir()):
            nested_path.rmdir()
            print(f"  🗑️  حذف دایرکتوری خالی: {nested_path.name}")
    
    print("\n✅ یکپارچه‌سازی تکمیل شد")

if __name__ == "__main__":
    flatten_nested_structure()