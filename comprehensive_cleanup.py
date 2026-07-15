#!/usr/bin/env python3
"""
اسکریپت جامع پاکسازی پروژه
- حذف فایل‌های scripts/ قدیمی
- حذف فایل‌های یتیم
- پاکسازی فایل‌های _remaining
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent

def backup_and_delete(file_path: Path, backup_dir: Path):
    """پشتیبان‌گیری و حذف فایل"""
    try:
        rel_path = file_path.relative_to(PROJECT_ROOT)
        backup_path = backup_dir / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        file_path.unlink()
        return True
    except Exception as e:
        print(f"❌ خطا: {file_path} - {e}")
        return False

def cleanup_scripts(backup_dir: Path):
    """حذف فایل‌های scripts/ قدیمی"""
    scripts_dir = PROJECT_ROOT / "scripts"
    if not scripts_dir.exists():
        return 0
    
    keep_files = {"seed_admin.py", "seed_data.py", "run_seed.py"}
    deleted = 0
    
    for file_path in scripts_dir.glob("*.py"):
        if file_path.name in keep_files:
            continue
        if backup_and_delete(file_path, backup_dir):
            deleted += 1
    
    return deleted

def cleanup_remaining_files(backup_dir: Path):
    """حذف فایل‌های _remaining.py"""
    deleted = 0
    
    for file_path in PROJECT_ROOT.rglob("*_remaining.py"):
        if backup_and_delete(file_path, backup_dir):
            deleted += 1
    
    return deleted

def cleanup_orphan_files(backup_dir: Path):
    """حذف فایل‌های یتیم"""
    # این تابع باید بر اساس نتایج find_broken_imports.py پیاده‌سازی شود
    # برای سادگی، فایل‌های scripts/ را حذف می‌کنیم
    return cleanup_scripts(backup_dir)

def main():
    backup_dir = PROJECT_ROOT / ".cleanup_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("🧹 شروع پاکسازی جامع پروژه")
    print("=" * 70)
    print(f"💾 Backup در: {backup_dir}\n")
    
    # مرحله ۱: حذف فایل‌های scripts/ قدیمی
    print("📝 مرحله ۱: حذف فایل‌های scripts/ قدیمی")
    deleted_scripts = cleanup_scripts(backup_dir)
    print(f"✅ {deleted_scripts} فایل حذف شد\n")
    
    # مرحله ۲: حذف فایل‌های _remaining.py
    print("📝 مرحله ۲: حذف فایل‌های _remaining.py")
    deleted_remaining = cleanup_remaining_files(backup_dir)
    print(f"✅ {deleted_remaining} فایل حذف شد\n")
    
    # خلاصه
    total_deleted = deleted_scripts + deleted_remaining
    print("=" * 70)
    print(f"✅ مجموعاً {total_deleted} فایل حذف شد")
    print("=" * 70)

if __name__ == "__main__":
    main()