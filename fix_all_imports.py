#!/usr/bin/env python3
"""
اسکریپت اصلاح کامل Import ها - نسخه نهایی
تمام import های apps.api.* را به app.* تبدیل می‌کند
"""

import re
from pathlib import Path

def fix_all_imports():
    """اصلاح تمام import ها در تمام فایل‌های Python"""
    
    # الگوهای جایگزینی
    patterns = [
        # از apps.api.xxx به app.xxx
        (r'from\s+apps\.api\.', 'from apps.app.'),
        (r'import\s+apps\.api\.', 'import apps.app.'),
        # از apps.api به app
        (r'from\s+apps\.api\s+import', 'from app import'),
        (r'import\s+apps\.api\s', 'import app '),
    ]
    
    # پیدا کردن تمام فایل‌های Python
    py_files = list(Path('.').rglob('*.py'))
    
    # حذف فایل‌های venv و backup
    py_files = [f for f in py_files if not any(skip in str(f) for skip in ['.venv', 'venv', 'backup', '_backup'])]
    
    total_files = 0
    total_changes = 0
    
    for file_path in py_files:
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # اعمال تمام الگوها
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            # اگر تغییری ایجاد شده
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                changes = sum(1 for p, r in patterns if re.search(p, original_content))
                total_files += 1
                total_changes += changes
                print(f"✅ {file_path}: تغییر {changes} import")
        
        except Exception as e:
            print(f"❌ خطا در {file_path}: {e}")
    
    print(f"\n✅ اصلاح شد {total_files} فایل")
    print(f"📝 مجموع تغییرات: {total_changes}")

if __name__ == "__main__":
    fix_all_imports()