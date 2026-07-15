#!/usr/bin/env python3
"""
fix_imports.py v3 - اصلاح کامل import ها
تبدیل apps.api.xxx به app.xxx
"""

import os
import re
from pathlib import Path
from typing import Tuple, List, Dict

# تنظیمات
PROJECT_ROOT = Path(__file__).parent
APPS_DIR = PROJECT_ROOT / "apps"

# الگوهای تبدیل (به ترتیب اولویت)
REPLACEMENTS = [
    # تبدیل apps.api.xxx به app.xxx
    (re.compile(r'from\s+apps\.api\.app\.'), 'from apps.app.'),
    (re.compile(r'import\s+apps\.api\.app\.'), 'import apps.app.'),
    (re.compile(r'from\s+apps\.api\.'), 'from apps.app.'),
    (re.compile(r'import\s+apps\.api\.'), 'import apps.app.'),
    
    # تبدیل مستقیم
    (re.compile(r'from\s+apps\.api\s+import'), 'from app import'),
    (re.compile(r'import\s+apps\.api\s'), 'import app '),
]

# دایرکتوری‌هایی که نباید پردازش شوند
SKIP_DIRS = {
    '.cleanup_backup',
    '.migration_backup',
    '.venv',
    'venv',
    '__pycache__',
    'node_modules',
    '.git',
}

def should_skip(path: Path) -> bool:
    """بررسی اینکه آیا باید از این مسیر صرف‌نظر شود"""
    parts = path.parts
    return any(skip in parts for skip in SKIP_DIRS)

def fix_file(file_path: Path) -> Tuple[int, List[str]]:
    """اصلاح import های یک فایل"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        changes = []
        
        for pattern, replacement in REPLACEMENTS:
            matches = pattern.findall(content)
            if matches:
                content = pattern.sub(replacement, content)
                changes.extend([f"{m.strip()} → {replacement.strip()}" for m in matches])
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return len(changes), changes
        
        return 0, []
    
    except Exception as e:
        print(f"  ❌ خطا در {file_path}: {e}")
        return 0, []

def main():
    print("=" * 70)
    print("🔧 اصلاح خودکار Import ها (نسخه ۳ - نهایی)")
    print("=" * 70)
    
    if not APPS_DIR.exists():
        print(f"❌ دایرکتوری {APPS_DIR} وجود ندارد")
        return
    
    # پیدا کردن فایل‌های Python فقط در apps/
    py_files = []
    for ext in ['*.py']:
        for f in APPS_DIR.rglob(ext):
            if not should_skip(f):
                py_files.append(f)
    
    print(f"📁 پیدا شد {len(py_files)} فایل Python در apps/")
    
    # پردازش فایل‌ها
    print("\n🔧 در حال اصلاح import ها...")
    total_changes = 0
    fixed_files = 0
    
    for file_path in py_files:
        changes_count, changes = fix_file(file_path)
        if changes_count > 0:
            fixed_files += 1
            total_changes += changes_count
            rel_path = file_path.relative_to(PROJECT_ROOT)
            print(f"  ✅ {rel_path}: تغییر {changes_count} import")
            for change in changes[:3]:  # نمایش 3 تغییر اول
                print(f"      {change}")
            if len(changes) > 3:
                print(f"      ... و {len(changes) - 3} تغییر دیگر")
    
    print("\n" + "=" * 70)
    print(f"✅ اصلاح شد {fixed_files} فایل")
    print(f"📝 مجموع تغییرات: {total_changes}")
    print("=" * 70)
    
    if fixed_files > 0:
        print("\n💡 برای بررسی مجدد:")
        print("   python find_broken_imports.py")

if __name__ == "__main__":
    main()