#!/usr/bin/env python3
"""
اسکریپت پاکسازی پروژه EconoJin
حذف فایل‌های _remaining.py و __init__.py تکراری
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

# مسیر پروژه
PROJECT_ROOT = Path(__file__).parent.resolve()

# Backend اصلی
BACKEND_ROOT = PROJECT_ROOT / "apps" / "api"

# پوشه backup
BACKUP_DIR = PROJECT_ROOT / ".cleanup_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")


def find_remaining_files() -> list[Path]:
    """یافتن تمام فایل‌های _remaining.py در backend"""
    remaining = []
    for path in BACKEND_ROOT.rglob("*_remaining.py"):
        remaining.append(path)
    return remaining


def find_duplicate_inits() -> list[Path]:
    """یافتن __init__.py تکراری بر اساس حجم"""
    size_map: dict[int, list[Path]] = {}
    
    for path in BACKEND_ROOT.rglob("__init__.py"):
        try:
            size = path.stat().st_size
            if size not in size_map:
                size_map[size] = []
            size_map[size].append(path)
        except Exception:
            continue
    
    duplicates = []
    for size, paths in size_map.items():
        if len(paths) > 1:
            # حفظ اولین، بقیه duplicate
            duplicates.extend(paths[1:])
    
    return duplicates


def backup_file(file_path: Path) -> bool:
    """پشتیبان‌گیری از فایل"""
    try:
        rel_path = file_path.relative_to(PROJECT_ROOT)
        backup_path = BACKUP_DIR / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        return True
    except Exception as e:
        print(f"  ❌ خطا در backup: {file_path} - {e}")
        return False


def delete_file(file_path: Path, backup_dir: Optional[Path], dry_run: bool) -> Tuple[bool, int]:
    """حذف فایل با backup"""
    try:
        size = file_path.stat().st_size
        
        if dry_run:
            return True, size
        
        if backup_dir:
            if not backup_file(file_path):
                return False, 0
        
        file_path.unlink()
        return True, size
    except Exception as e:
        print(f"  ❌ خطا در حذف: {file_path} - {e}")
        return False, 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="پاکسازی پروژه EconoJin")
    parser.add_argument("--only-remaining", action="store_true", help="فقط حذف _remaining.py")
    parser.add_argument("--only-inits", action="store_true", help="فقط حذف __init__.py تکراری")
    parser.add_argument("--backup", action="store_true", help="ایجاد backup")
    parser.add_argument("--dry-run", action="store_true", help="فقط نمایش، بدون حذف")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🧹 پاکسازی پروژه EconoJin")
    print("=" * 70)
    print(f"📁 Backend: {BACKEND_ROOT}")
    print(f"💾 Backup: {'فعال' if args.backup else 'غیرفعال'}")
    print(f"🔍 Dry-run: {'بله' if args.dry_run else 'خیر'}")
    print("=" * 70)
    
    # ایجاد پوشه backup
    if args.backup and not args.dry_run:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        print(f"💾 پوشه backup: {BACKUP_DIR}")
    
    total_deleted = 0
    total_size = 0
    
    # حذف _remaining.py
    if not args.only_inits:
        print("\n📝 حذف فایل‌های _remaining.py...")
        remaining = find_remaining_files()
        print(f"   یافت شد: {len(remaining)} فایل")
        
        for path in remaining:
            success, size = delete_file(path, BACKUP_DIR if args.backup else None, args.dry_run)
            if success:
                total_deleted += 1
                total_size += size
                if not args.dry_run:
                    print(f"   ✅ حذف شد: {path.relative_to(PROJECT_ROOT)}")
    
    # حذف __init__.py تکراری
    if not args.only_remaining:
        print("\n📄 حذف __init__.py تکراری...")
        duplicates = find_duplicate_inits()
        print(f"   یافت شد: {len(duplicates)} فایل تکراری")
        
        for path in duplicates:
            success, size = delete_file(path, BACKUP_DIR if args.backup else None, args.dry_run)
            if success:
                total_deleted += 1
                total_size += size
                if not args.dry_run:
                    print(f"   ✅ حذف شد: {path.relative_to(PROJECT_ROOT)}")
    
    # خلاصه
    print("\n" + "=" * 70)
    print("📊 خلاصه")
    print("=" * 70)
    print(f"✅ تعداد حذف شده: {total_deleted}")
    print(f"📦 حجم آزاد شده: {total_size / 1024:.2f} KB")
    
    if args.dry_run:
        print("\n💡 این dry-run بود. برای حذف واقعی:")
        print("   python fix_project.py --backup")
    elif args.backup:
        print(f"\n💾 Backup در: {BACKUP_DIR}")
    
    print("=" * 70)


if __name__ == "__main__":
    main()