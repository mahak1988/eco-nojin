#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏗️ Econojin Project Restructurer
سازماندهی فایل‌ها در ساختار استاندارد
"""
import sys, shutil
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

# ساختار هدف پروژه
TARGET_STRUCTURE = {
    'api/': ['*.py'],  # همه فایل‌های پایتون بک‌اند
    'web/': ['*.tsx', '*.ts', '*.css', 'package.json', 'next.config.js'],
    'docs/': ['*.md', '*.txt'],
    'scripts/': ['*.py', '*.ps1', '*.sh'],
    'infrastructure/': ['*.yml', '*.yaml', 'Dockerfile*', 'docker-compose*'],
}

def find_files_by_pattern(patterns: list) -> list:
    """یافتن فایل‌ها بر اساس الگو"""
    found = []
    for pat in patterns:
        if pat.startswith('*.'):
            found.extend(ROOT.rglob(pat))
        else:
            p = ROOT / pat
            if p.exists():
                found.append(p)
    return found

def move_to_target(file_path: Path, target_dir: str) -> bool:
    """انتقال فایل به پوشه هدف"""
    try:
        target = ROOT / target_dir.rstrip('/') / file_path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target != file_path:
            # جلوگیری از بازنویسی تصادفی
            target = target.with_stem(f"{target.stem}_moved")
        shutil.move(str(file_path), str(target))
        return True
    except Exception as e:
        print(f"   ❌ {file_path.name}: {e}")
        return False

def restructure(dry_run: bool = True) -> dict:
    """اجرای سازماندهی"""
    stats = {'moved': 0, 'skipped': 0, 'errors': 0}
    
    print(f"{'🔍' if dry_run else '🔄'} Analyzing file locations...")
    
    for target_dir, patterns in TARGET_STRUCTURE.items():
        files = find_files_by_pattern(patterns)
        # فیلتر: فقط فایل‌هایی که الان در جای درست نیستند
        misplaced = [f for f in files if target_dir.rstrip('/') not in f.parts]
        
        for file_path in misplaced:
            # نادیده گرفتن node_modules و .venv
            if any(ign in file_path.parts for ign in ['node_modules', '.venv', 'tutorial_env']):
                stats['skipped'] += 1
                continue
            if dry_run:
                print(f"   Would move: {file_path.relative_to(ROOT)} → {target_dir}")
            else:
                if move_to_target(file_path, target_dir):
                    stats['moved'] += 1
                    print(f"   ✓ {file_path.name} → {target_dir}")
                else:
                    stats['errors'] += 1
    
    return stats

def main():
    print("🏗️ Econojin Project Restructurer")
    print("=" * 50)
    
    # مرحله ۱: پیش‌نمایش
    print("\n[1/2] Preview mode:")
    stats = restructure(dry_run=True)
    
    print(f"\n📊 Preview:")
    print(f"   Would move: {stats['moved']} files")
    print(f"   Skipped (in node_modules/etc): {stats['skipped']}")
    
    if stats['moved'] == 0:
        print("\n✅ Project structure looks good!")
        return 0
    
    # مرحله ۲: تایید
    print(f"\n⚠️  Restructure project?")
    print(f"   Type 'YES' to confirm:")
    if input("   > ").strip() != 'YES':
        print("\n❌ Cancelled.")
        return 0
    
    # مرحله ۳: اجرا
    print(f"\n[2/2] Executing...")
    stats = restructure(dry_run=False)
    
    print(f"\n✅ Restructure Complete:")
    print(f"   Moved: {stats['moved']} files")
    print(f"   Errors: {stats['errors']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())