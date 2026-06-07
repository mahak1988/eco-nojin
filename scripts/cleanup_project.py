#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 Econojin Project Cleanup
حذف فایل‌ها و پوشه‌های غیرضروری برای سبک‌سازی پروژه
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

# پوشه‌هایی که باید حذف یا نادیده گرفته شوند
TO_REMOVE = [
    "tutorial_env",  # محیط مجازی آموزشی - غیرضروری
    "temp",
    "tmp",
    ".temp",
    "backup",
    "backups",
    "*.log",
    "*.tmp",
    "*.bak",
]

# پوشه‌های استاندارد که باید حفظ شوند
KEEP_DIRS = {
    "api",
    "apps",
    "web",
    "src",
    "docs",
    "scripts",
    "infrastructure",
    "tests",
    "public",
    "node_modules",
    ".venv",
}


def should_remove(path: Path) -> bool:
    """تصمیم‌گیری برای حذف"""
    name = path.name.lower()
    # حذف بر اساس نام
    if name in {"tutorial_env", "temp", "tmp", "backup", "backups"}:
        return True
    if name.startswith(".") and name not in {".git", ".github", ".vscode"}:
        return True
    # حذف بر اساس پسوند
    if path.suffix.lower() in {".log", ".tmp", ".bak", ".swp"}:
        return True
    # حذف فایل‌های گزارش قدیمی
    if "report" in name and path.suffix in {".md", ".txt", ".json"}:
        if path.stat().st_size > 500_000:  # گزارش‌های بزرگ قدیمی
            return True
    return False


def cleanup(dry_run: bool = True) -> dict:
    """اجرای پاک‌سازی"""
    stats = {"removed": 0, "saved_bytes": 0, "errors": 0}

    print(f"{'🔍' if dry_run else '🗑️'} Scanning {ROOT}...")

    for path in sorted(ROOT.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if not path.exists():
            continue
        if any(keep in path.parts for keep in KEEP_DIRS):
            if path.is_dir() and path.name not in KEEP_DIRS:
                continue
        if should_remove(path):
            try:
                size = path.stat().st_size if path.is_file() else 0
                if dry_run:
                    print(f"   Would remove: {path.relative_to(ROOT)} ({size:,}B)")
                else:
                    if path.is_dir():
                        shutil.rmtree(path)
                        print(f"   🗑️  Dir: {path.relative_to(ROOT)}")
                    else:
                        path.unlink()
                        print(f"   🗑️  File: {path.relative_to(ROOT)}")
                stats["removed"] += 1
                stats["saved_bytes"] += size
            except Exception as e:
                print(f"   ❌ Error: {path} - {e}")
                stats["errors"] += 1

    return stats


def main():
    print("🧹 Econojin Project Cleanup")
    print("=" * 50)

    # مرحله ۱: پیش‌نمایش (dry-run)
    print("\n[1/2] Preview mode (nothing will be deleted):")
    stats = cleanup(dry_run=True)

    print(f"\n📊 Preview Summary:")
    print(f"   Would remove: {stats['removed']} items")
    print(f"   Would save: {stats['saved_bytes'] / 1_000_000:.1f} MB")

    if stats["removed"] == 0:
        print("\n✅ Nothing to clean up!")
        return 0

    # مرحله ۲: تایید کاربر
    print(f"\n⚠️  Proceed with deletion?")
    print(f"   Type 'YES' to confirm, or anything else to cancel:")
    confirm = input("   > ").strip()

    if confirm != "YES":
        print("\n❌ Cancelled.")
        return 0

    # مرحله ۳: اجرای واقعی
    print(f"\n[2/2] Executing cleanup...")
    stats = cleanup(dry_run=False)

    print(f"\n✅ Cleanup Complete:")
    print(f"   Removed: {stats['removed']} items")
    print(f"   Saved: {stats['saved_bytes'] / 1_000_000:.1f} MB")
    if stats["errors"]:
        print(f"   Errors: {stats['errors']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
