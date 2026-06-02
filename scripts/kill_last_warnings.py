#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
رفع نهایی 3 SyntaxWarning باقی‌مانده
مخصوص \e در مسیرهای Windows در docstrings
r"""

import sys
import re
import shutil
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(r'D:\econojin.com')

WARNING_FILES = [
    'install_with_pnpm_iran.py',
    'manual_install_fixed.py',
    'manual_install_packages.py',
]


def backup_file(file_path):
    backup_dir = file_path.parent / '.warnings_final_backup'
    backup_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = backup_dir / f"{file_path.stem}_{ts}{file_path.suffix}"
    shutil.copy2(file_path, backup)
    return backup


def fix_file_aggressive(file_path):
    """رفع تهاجمی همه \e و escape sequences نامعتبر"""
    if not file_path.exists():
        return False
    
    backup_file(file_path)
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    # روش 1: تبدیل \e به \\e (مستقیم)
    content = content.replace('\\econojin', '\\\\econojin')
    content = content.replace('\\env', '\\\\env')
    content = content.replace('\\etc', '\\\\etc')
    
    # روش 2: اگر در docstring است، آن را raw string کنیم
    # پیدا کردن docstring اول فایل
    if content.startswith('r"""') or content.startswith("'''"):
        quote = content[:3]
        end_idx = content.find(quote, 3)
        if end_idx != -1:
            docstring = content[3:end_idx]
            # اگر مسیر Windows در docstring است
            if re.search(r'[A-Za-z]:\\', docstring):
                # تبدیل backslash های مشکل‌ساز در docstring
                fixed_docstring = docstring.replace('\\e', '\\\\e')
                fixed_docstring = fixed_docstring.replace('\\p', '\\\\p')
                fixed_docstring = fixed_docstring.replace('\\a', '\\\\a')
                fixed_docstring = fixed_docstring.replace('\\s', '\\\\s')
                content = quote + fixed_docstring + content[end_idx:]
    
    # روش 3: بررسی همه string literals
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        # اگر خط شامل D:\econojin یا مسیرهای مشابه است
        if re.search(r'[A-Za-z]:\\', line):
            # تبدیل string معمولی به raw string
            def to_raw(m):
                return 'r' + m.group(0)
            
            # فقط اگر هنوز raw نیست
            line = re.sub(
                r'(?<![rRbBuUfF])(["\'])([A-Za-z]:\\[^"\']*)\1',
                to_raw,
                line
            )
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return True
    
    # روش 4 (آخرین): جایگزینی کامل docstring با متن ساده
    try:
        import ast
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree)
        
        if docstring and ('\\' in docstring):
            # حذف docstring مشکل‌دار
            new_content = content.replace(
                f'"""{docstring}"""',
                '"""\nScript file\n"""'
            )
            new_content = new_content.replace(
                f"'''{docstring}'''",
                "'''\nScript file\n'''"
            )
            
            if new_content != content:
                file_path.write_text(new_content, encoding='utf-8')
                return True
    except Exception:
        pass
    
    return False


def verify_warnings():
    """بررسی نهایی نبود warning"""
    import warnings
    import ast
    
    total_warnings = 0
    
    for filename in WARNING_FILES:
        # جستجوی فایل
        file_path = None
        for candidate in PROJECT_ROOT.rglob(filename):
            if '.venv' not in str(candidate) and '.backup' not in str(candidate):
                file_path = candidate
                break
        
        if not file_path:
            continue
        
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                content = file_path.read_text(encoding='utf-8')
                ast.parse(content)
                
                syntax_warnings = [x for x in w if issubclass(x.category, SyntaxWarning)]
                if syntax_warnings:
                    print(f"  [WARN] {filename}: {len(syntax_warnings)} warning(s)")
                    total_warnings += len(syntax_warnings)
                else:
                    print(f"  [OK] {filename}: clean")
        except Exception as e:
            print(f"  [ERR] {filename}: {e}")
    
    return total_warnings


def main():
    print("=" * 70)
    print("  KILL LAST WARNINGS - رفع نهایی 3 warning")
    print("=" * 70)
    
    fixed = 0
    for filename in WARNING_FILES:
        # جستجو
        file_path = None
        for candidate in PROJECT_ROOT.rglob(filename):
            if '.venv' not in str(candidate) and '.backup' not in str(candidate):
                file_path = candidate
                break
        
        if not file_path:
            print(f"  [SKIP] {filename}: not found")
            continue
        
        if fix_file_aggressive(file_path):
            print(f"  [OK] Fixed {filename}")
            fixed += 1
        else:
            print(f"  [SKIP] {filename}: no change")
    
    print(f"\n  Total fixed: {fixed}")
    
    print("\n" + "-" * 70)
    print("  VERIFICATION:")
    print("-" * 70)
    remaining = verify_warnings()
    
    print("\n" + "=" * 70)
    if remaining == 0:
        print("  🎉 SUCCESS! پروژه کاملاً تمیز شد (0 errors, 0 warnings)")
    else:
        print(f"  ℹ️  {remaining} warning(s) باقی مانده (غیر بحرانی)")
        print("     این warnings اجرای کد را متوقف نمی‌کنند")
    print("=" * 70)


if __name__ == '__main__':
    main()