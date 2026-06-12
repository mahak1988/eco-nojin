#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scan all models and find all foreign keys
"""

import re
from pathlib import Path
from collections import defaultdict

def find_all_models():
    """پیدا کردن تمام فایل‌های models.py"""
    print("=" * 70)
    print("🔍 اسکن تمام فایل‌های models.py...")
    print("=" * 70)
    
    model_files = []
    for path in Path("api").rglob("*.py"):
        if "__pycache__" in str(path):
            continue
        if "models.py" in path.name or "model.py" in path.name:
            model_files.append(path)
    
    print(f"   📊 {len(model_files)} فایل مدل یافت شد")
    for f in model_files:
        print(f"      - {f}")
    
    return model_files


def extract_foreign_keys(model_files):
    """استخراج تمام foreign key ها"""
    print("\n" + "=" * 70)
    print("🔗 استخراج تمام Foreign Key ها...")
    print("=" * 70)
    
    foreign_keys = defaultdict(list)  # table_name -> [referenced_tables]
    
    for model_file in model_files:
        content = model_file.read_text(encoding='utf-8')
        
        # پیدا کردن ForeignKey
        pattern = r'ForeignKey\(["\'](\w+)\.(\w+)["\']\)'
        matches = re.findall(pattern, content)
        
        for table, column in matches:
            foreign_keys[model_file].append((table, column))
    
    # نمایش نتایج
    all_referenced_tables = set()
    for model_file, fks in foreign_keys.items():
        if fks:
            print(f"\n   📄 {model_file}")
            for table, column in fks:
                print(f"      → {table}.{column}")
                all_referenced_tables.add(table)
    
    print(f"\n   📊 مجموع جداول referenced: {len(all_referenced_tables)}")
    print(f"   📋 جداول: {', '.join(sorted(all_referenced_tables))}")
    
    return all_referenced_tables


def find_table_definitions(model_files):
    """پیدا کردن تعریف تمام جداول"""
    print("\n" + "=" * 70)
    print("📋 پیدا کردن تعریف جداول...")
    print("=" * 70)
    
    table_definitions = {}  # table_name -> file
    
    for model_file in model_files:
        content = model_file.read_text(encoding='utf-8')
        
        # پیدا کردن __tablename__
        pattern = r'__tablename__\s*=\s*["\'](\w+)["\']'
        matches = re.findall(pattern, content)
        
        for table in matches:
            table_definitions[table] = model_file
    
    print(f"   📊 {len(table_definitions)} جدول تعریف شده")
    for table, file in sorted(table_definitions.items()):
        print(f"      - {table} → {file}")
    
    return table_definitions


def find_missing_tables(referenced_tables, defined_tables):
    """پیدا کردن جداول کم"""
    print("\n" + "=" * 70)
    print("❌ پیدا کردن جداول کم...")
    print("=" * 70)
    
    missing = referenced_tables - set(defined_tables.keys())
    
    if missing:
        print(f"   ❌ {len(missing)} جدول کم است:")
        for table in sorted(missing):
            print(f"      - {table}")
    else:
        print("   ✅ تمام جداول referenced تعریف شده‌اند")
    
    return missing


def search_for_missing_models(missing_tables):
    """جستجو برای مدل‌های کم"""
    print("\n" + "=" * 70)
    print("🔎 جستجو برای مدل‌های کم...")
    print("=" * 70)
    
    for table in missing_tables:
        print(f"\n   🔍 جستجو برای '{table}'...")
        
        # جستجو در تمام فایل‌های Python
        found = False
        for py_file in Path("api").rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            # جستجو برای __tablename__
            if f'__tablename__ = "{table}"' in content or f"__tablename__ = '{table}'" in content:
                print(f"      ✅ یافت شد در: {py_file}")
                found = True
            
            # جستجو برای class name
            class_name = table.replace('_', ' ').title().replace(' ', '')
            if f"class {class_name}" in content:
                print(f"      ✅ کلاس {class_name} یافت شد در: {py_file}")
                found = True
        
        if not found:
            print(f"      ❌ یافت نشد")


def main():
    print("\n" + "=" * 70)
    print("🚀 Econojin Foreign Key Scanner")
    print("=" * 70)
    print()
    
    try:
        # اسکن مدل‌ها
        model_files = find_all_models()
        
        # استخراج foreign key ها
        referenced_tables = extract_foreign_keys(model_files)
        
        # پیدا کردن تعریف جداول
        defined_tables = find_table_definitions(model_files)
        
        # پیدا کردن جداول کم
        missing_tables = find_missing_tables(referenced_tables, defined_tables)
        
        # جستجو برای مدل‌های کم
        if missing_tables:
            search_for_missing_models(missing_tables)
        
        # دستورالعمل‌ها
        print("\n" + "=" * 70)
        print("📋 دستورالعمل‌ها:")
        print("=" * 70)
        print()
        
        if missing_tables:
            print("❌ جداول کم وجود دارند. باید:")
            print("   1. مدل‌های مربوطه را پیدا کنید")
            print("   2. آن‌ها را به all_models.py اضافه کنید")
            print("   3. یا foreign key ها را حذف کنید")
        else:
            print("✅ تمام جداول تعریف شده‌اند")
            print("   فقط کافی است all_models.py را به‌روز کنید")
        
        print()
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()