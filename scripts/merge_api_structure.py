#!/usr/bin/env python3
"""
اسکریپت ادغام ساختار api
ادغام modules, services, routers, scientific_core با domains
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field

# ──────────────────────────────────────────────────────────────
# پیکربندی
# ──────────────────────────────────────────────────────────────
API_ROOT = Path("D:/econojin.com/api")
BACKUP_DIR = Path("D:/econojin.com/.structure_backup") / datetime.now().strftime("%Y%m%d_%H%M%S")

# دایرکتوری‌هایی که باید ادغام شوند
MERGE_DIRS = {
    "modules": "domains",
    "services": "domains",
    "routers": "domains",
    "scientific_core": "domains",
}

# ──────────────────────────────────────────────────────────────
# ساختار داده
# ──────────────────────────────────────────────────────────────
@dataclass
class MergeAction:
    action: str  # "move", "skip", "backup"
    source: str
    destination: str
    reason: str
    is_duplicate: bool = False

@dataclass
class MergeReport:
    actions: List[MergeAction] = field(default_factory=list)
    duplicates_found: int = 0
    files_moved: int = 0
    files_skipped: int = 0
    errors: List[str] = field(default_factory=list)

# ──────────────────────────────────────────────────────────────
# توابع کمکی
# ──────────────────────────────────────────────────────────────
def get_file_hash(file_path: Path) -> str:
    """محاسبه hash ساده برای تشخیص تکراری"""
    try:
        size = file_path.stat().st_size
        return f"{size}_{file_path.name}"
    except:
        return ""

def backup_file(source: Path, backup_root: Path) -> bool:
    """پشتیبان‌گیری از فایل"""
    try:
        rel = source.relative_to(API_ROOT)
        dest = backup_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        return True
    except Exception as e:
        print(f"  ⚠️  خطا در backup: {source} - {e}")
        return False

# ──────────────────────────────────────────────────────────────
# تحلیل و ادغام
# ──────────────────────────────────────────────────────────────
def analyze_merge(source_dir: str, target_dir: str, report: MergeReport):
    """تحلیل و برنامه‌ریزی ادغام"""
    source_path = API_ROOT / source_dir
    target_path = API_ROOT / target_dir
    
    if not source_path.exists():
        print(f"  ⚠️  دایرکتوری {source_dir} وجود ندارد")
        return
    
    print(f"\n📂 تحلیل {source_dir} → {target_dir}")
    print("-" * 60)
    
    # جمع‌آوری hash فایل‌های موجود در target
    existing_files: Dict[str, Path] = {}
    if target_path.exists():
        for file in target_path.rglob("*"):
            if file.is_file():
                hash_val = get_file_hash(file)
                if hash_val:
                    existing_files[hash_val] = file
    
    # پردازش فایل‌های source
    for file in source_path.rglob("*"):
        if not file.is_file():
            continue
        
        rel_path = file.relative_to(source_path)
        target_file = target_path / rel_path
        hash_val = get_file_hash(file)
        
        # بررسی تکراری بودن
        if hash_val in existing_files:
            report.actions.append(MergeAction(
                action="skip",
                source=str(file),
                destination=str(target_file),
                reason="فایل تکراری - حذف می‌شود",
                is_duplicate=True
            ))
            report.duplicates_found += 1
        elif target_file.exists():
            # فایل با نام یکسان اما محتوای متفاوت
            report.actions.append(MergeAction(
                action="backup",
                source=str(file),
                destination=str(target_file),
                reason="فایل با نام یکسان وجود دارد - backup و جایگزینی"
            ))
        else:
            # فایل جدید - منتقل شود
            report.actions.append(MergeAction(
                action="move",
                source=str(file),
                destination=str(target_file),
                reason="انتقال به domains"
            ))

def execute_merge(report: MergeReport, dry_run: bool = True):
    """اجرای عملیات ادغام"""
    if not dry_run:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        print(f"\n💾 Backup در: {BACKUP_DIR}")
    
    for action in report.actions:
        source = Path(action.source)
        dest = Path(action.destination)
        
        if dry_run:
            print(f"  🔍 {action.action.upper()}: {action.source}")
            print(f"     └─ {action.reason}")
            continue
        
        try:
            if action.action == "skip":
                # حذف فایل تکراری
                if source.exists():
                    source.unlink()
                    report.files_skipped += 1
                    print(f"  🗑️  حذف تکراری: {action.source}")
            
            elif action.action == "backup":
                # backup فایل موجود و جایگزینی
                if dest.exists():
                    backup_file(dest, BACKUP_DIR)
                    dest.unlink()
                
                if source.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source), str(dest))
                    report.files_moved += 1
                    print(f"  📦 backup و جایگزینی: {action.source}")
            
            elif action.action == "move":
                # انتقال ساده
                if source.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source), str(dest))
                    report.files_moved += 1
                    print(f"  ➡️  انتقال: {action.source} → {action.destination}")
        
        except Exception as e:
            error_msg = f"خطا در {action.source}: {e}"
            report.errors.append(error_msg)
            print(f"  ❌ {error_msg}")
    
    # حذف دایرکتوری‌های خالی
    if not dry_run:
        for source_dir in MERGE_DIRS.keys():
            source_path = API_ROOT / source_dir
            if source_path.exists():
                try:
                    # حذف دایرکتوری‌های خالی
                    for dirpath, dirnames, filenames in os.walk(source_path, topdown=False):
                        if not os.listdir(dirpath):
                            os.rmdir(dirpath)
                    
                    # اگر دایرکتوری اصلی خالی است، حذف شود
                    if not os.listdir(source_path):
                        os.rmdir(source_path)
                        print(f"  🗑️  حذف دایرکتوری خالی: {source_dir}")
                except Exception as e:
                    print(f"  ⚠️  خطا در حذف دایرکتوری {source_dir}: {e}")

# ──────────────────────────────────────────────────────────────
# رابط کاربری
# ──────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("🔧 اسکریپت ادغام ساختار api")
    print("=" * 70)
    
    report = MergeReport()
    
    # تحلیل تمام دایرکتوری‌ها
    for source_dir, target_dir in MERGE_DIRS.items():
        analyze_merge(source_dir, target_dir, report)
    
    # خلاصه
    print("\n" + "=" * 70)
    print("📊 خلاصه تحلیل")
    print("=" * 70)
    print(f"  فایل‌های تکراری: {report.duplicates_found}")
    print(f"  فایل‌های برای انتقال: {sum(1 for a in report.actions if a.action == 'move')}")
    print(f"  فایل‌های برای backup: {sum(1 for a in report.actions if a.action == 'backup')}")
    print(f"  فایل‌های برای حذف: {sum(1 for a in report.actions if a.action == 'skip')}")
    
    if not report.actions:
        print("\n✅ هیچ عملیاتی لازم نیست!")
        return
    
    # پرسش برای اجرا
    print("\n" + "=" * 70)
    mode = input("🔍 حالت اجرا (dry-run/execute): ").strip().lower()
    
    if mode not in ["dry-run", "execute"]:
        print("❌ ورودی نامعتبر")
        return
    
    dry_run = (mode == "dry-run")
    
    if not dry_run:
        confirm = input("⚠️  آیا مطمئن هستید؟ (yes/no): ").strip().lower()
        if confirm != "yes":
            print("❌ لغو شد")
            return
    
    # اجرا
    print("\n" + "=" * 70)
    print(f"🚀 شروع اجرای {'آزمایشی' if dry_run else 'واقعی'}")
    print("=" * 70)
    
    execute_merge(report, dry_run)
    
    # خلاصه نهایی
    print("\n" + "=" * 70)
    print("✅ خلاصه نهایی")
    print("=" * 70)
    print(f"  فایل‌های منتقل شده: {report.files_moved}")
    print(f"  فایل‌های حذف شده: {report.files_skipped}")
    
    if report.errors:
        print(f"\n⚠️  {len(report.errors)} خطا رخ داد:")
        for error in report.errors[:10]:
            print(f"  - {error}")
        if len(report.errors) > 10:
            print(f"  ... و {len(report.errors) - 10} خطای دیگر")
    
    if not dry_run:
        print(f"\n💾 Backup در: {BACKUP_DIR}")

if __name__ == "__main__":
    main()