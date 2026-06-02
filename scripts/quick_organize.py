#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗂️ Econojin Quick Organizer
جابجایی هوشمند فایل‌های حیاتی به ساختار استاندارد
"""
import sys, shutil
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

# نگاشت: الگوی نام فایل → پوشه هدف
MOVE_RULES = {
    # اسکریپت‌های ریشه → scripts/
    ('*.py', 'root'): 'scripts/',
    # فایل‌های پیکربندی ریشه → حفظ شوند
    ('package.json', 'root'): None,  # None = حفظ در ریشه
    ('requirements.txt', 'root'): None,
    ('README.md', 'root'): None,
    # فایل‌های فرانت‌اند پراکنده → web/
    ('*.tsx', 'any'): 'web/src/app/',
    ('*.ts', 'any'): 'web/src/lib/',
    ('*.css', 'any'): 'web/src/styles/',
    # فایل‌های بک‌اند پراکنده → api/
    ('main.py', 'any'): 'api/',
    ('config.py', 'any'): 'api/core/',
    ('database.py', 'any'): 'api/core/',
    ('router.py', 'any'): 'api/modules/',
}

def get_target(file_path: Path) -> Path | None:
    """تعیین پوشه هدف برای یک فایل"""
    name = file_path.name
    suffix = file_path.suffix
    rel_parts = file_path.relative_to(ROOT).parts
    
    # فایل در ریشه است؟
    is_root = len(rel_parts) == 1
    
    for (pattern, location), target in MOVE_RULES.items():
        if target is None:  # حفظ فایل در جای فعلی
            if pattern == name and (location == 'root' and is_root):
                return None
        
        # تطبیق الگو
        if pattern == '*' + suffix or pattern == name:
            if location == 'root' and not is_root:
                continue
            if target:
                return ROOT / target.rstrip('/')
    return None

def organize(dry_run: bool = True) -> dict:
    stats = {'moved': 0, 'kept': 0, 'errors': 0}
    
    # فقط فایل‌های لایه اول و دوم را اسکن کن (سرعت بیشتر)
    for depth in [1, 2]:
        for path in ROOT.iterdir():
            if depth == 2 and path.is_dir():
                for sub in path.iterdir():
                    if sub.is_file() and sub.suffix in {'.py', '.tsx', '.ts', '.css', '.json'}:
                        target = get_target(sub)
                        if target and target != sub.parent:
                            stats['moved'] += _move_file(sub, target, dry_run)
            elif path.is_file():
                target = get_target(path)
                if target is None:
                    stats['kept'] += 1
                elif target and target != path.parent:
                    stats['moved'] += _move_file(path, target, dry_run)
    
    return stats

def _move_file(src: Path, target_dir: Path, dry_run: bool) -> int:
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / src.name
        if dest.exists() and dest != src:
            dest = dest.with_stem(f"{dest.stem}_org")
        if dry_run:
            print(f"   → {src.relative_to(ROOT)} → {dest.relative_to(ROOT)}")
        else:
            shutil.move(str(src), str(dest))
            print(f"   ✓ {src.name}")
        return 1
    except Exception as e:
        print(f"   ❌ {src.name}: {e}")
        return 0

def main():
    print("🗂️ Econojin Quick Organizer")
    print("=" * 50)
    
    print("\n[1/2] Preview:")
    stats = organize(dry_run=True)
    print(f"\n📊 Would move: {stats['moved']} files")
    
    if stats['moved'] == 0:
        print("✅ No files need reorganization!")
        return 0
    
    print(f"\n⚠️  Proceed? Type 'YES' to confirm:")
    if input("   > ").strip() != 'YES':
        print("\n❌ Cancelled.")
        return 0
    
    print(f"\n[2/2] Executing...")
    stats = organize(dry_run=False)
    print(f"\n✅ Moved: {stats['moved']} files")
    return 0

if __name__ == "__main__":
    sys.exit(main())