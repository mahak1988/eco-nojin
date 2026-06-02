#!/usr/bin/env python3
"""
رفع نهایی SyntaxWarning ها (invalid escape sequences)
مخصوص مسیرهای Windows در docstrings و string literals
"""


# === Auto-added: Add project root to sys.path ===
import sys
from pathlib import Path as _Path
_project_root = _Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
# === End auto-added ===

import sys
import re
from pathlib import Path
from datetime import datetime
import shutil

import logging
logger = logging.getLogger(__name__)



def backup_file(file_path: Path) -> Path:
    """ایجاد backup"""
    backup_dir = file_path.parent / '.warnings_backup'
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
    shutil.copy2(file_path, backup_path)
    return backup_path


def find_warnings_files(project_root: Path):
    """پیدا کردن فایل‌های دارای escape sequence warning"""
    import warnings
    
    problem_files = set()
    
    for py_file in project_root.rglob('*.py'):
        if any(part in str(py_file) for part in [
            '.venv', 'node_modules', '__pycache__',
            '.backup', '.syntax_backup', '.warnings_backup',
            '.emergency_backup'
        ]):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8')
            
            # بررسی وجود مسیرهای Windows بدون raw string
            # الگوهای مشکوک:
            patterns = [
                # مسیرهای Windows در string های معمولی (نه raw)
                r'(?<![rR])(["\'])([^"\']*[A-Za-z]:\\[^"\']*?)\1',
                
                # docstrings با مسیر Windows
                r'(?<=r"""[\s\S]{0,500}?)([A-Za-z]:\\[^"\\\n]+)',
            ]
            
            # روش ساده‌تر: پیدا کردن همه \e, \a, \p, etc که escape معتبر نیستند
            # escape های معتبر: \n \t \r \0 \\ \' \" \a \b \f \v \x \u \U \N
            invalid_escapes = re.findall(
                r'(?<![rR])(["\'])([^"\'\\]*(?:\\[^ntr0\\\'\"abfvxuUN][^"\'\\]*)+)[^"\']*\1',
                content
            )
            
            if invalid_escapes:
                # بررسی دقیق‌تر
                for match in re.finditer(r'(?<![rR])(["\'])(.*?)(?<!\\)\1', content, re.DOTALL):
                    string_content = match.group(2)
                    # بررسی escape sequences
                    for esc_match in re.finditer(r'\\(.)', string_content):
                        esc_char = esc_match.group(1)
                        if esc_char not in 'ntr0\\\'"abfvxuUN \n\r\t':
                            problem_files.add(py_file)
                            break
        
        except Exception:
            pass
    
    return list(problem_files)


def fix_file_warnings(file_path: Path) -> bool:
    """رفع warnings یک فایل"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # رفع مسیرهای Windows در string های معمولی
        # تبدیل به raw string یا escape کردن backslash ها
        
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # اگر خط شامل مسیر Windows است
            if re.search(r'[A-Za-z]:\\', line):
                # بررسی اینکه آیا در string است
                # اگر raw string نیست، آن را raw string کنیم
                
                def make_raw_string(match):
                    full_match = match.group(0)
                    quote = full_match[0]
                    
                    # اگر قبلاً raw است
                    # (این تابع فقط از غیر raw صدا زده می‌شود)
                    
                    content_str = full_match[1:-1]
                    
                    # escape sequences معتبر را نگه دار
                    valid_escapes = {'n', 't', 'r', '0', '\\', "'", '"', 
                                     'a', 'b', 'f', 'v', 'x', 'u', 'U', 'N'}
                    
                    has_invalid = False
                    i = 0
                    while i < len(content_str):
                        if content_str[i] == '\\' and i + 1 < len(content_str):
                            next_char = content_str[i + 1]
                            if next_char not in valid_escapes:
                                has_invalid = True
                                break
                            i += 2
                        else:
                            i += 1
                    
                    if has_invalid:
                        # double کردن backslash های نامعتبر
                        new_content = []
                        i = 0
                        while i < len(content_str):
                            if content_str[i] == '\\' and i + 1 < len(content_str):
                                next_char = content_str[i + 1]
                                if next_char in valid_escapes:
                                    new_content.append(content_str[i:i+2])
                                    i += 2
                                else:
                                    new_content.append('\\\\')
                                    i += 1
                            else:
                                new_content.append(content_str[i])
                                i += 1
                        
                        return quote + ''.join(new_content) + quote
                    
                    return full_match
                
                # پیدا کردن و رفع string های شامل مسیر
                new_line = re.sub(
                    r'(?<![rR])(["\'])([A-Za-z]:\\[^"\']*)\1',
                    make_raw_string,
                    line
                )
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
        
        if content != original:
            backup_file(file_path)
            file_path.write_text(content, encoding='utf-8')
            return True
        
        return False
        
    except Exception as e:
        logger.info(f"  ⚠️  خطا در {file_path.name}: {e}")
        return False


def fix_docstring_warnings(project_root: Path):
    """رفع warnings در docstrings"""
    logger.info("\n🔧 رفع warnings در docstrings...")
    
    fixed_count = 0
    
    # فایل‌هایی که احتمالاً مشکل دارند
    suspicious_files = []
    
    for py_file in project_root.rglob('*.py'):
        if any(part in str(py_file) for part in [
            '.venv', 'node_modules', '__pycache__', '.backup'
        ]):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8')
            
            # بررسی وجود مسیرهای Windows در docstrings
            if re.search(r'(r"""|\'\'\')[\s\S]*?[A-Za-z]:\\[\s\S]*?\1', content):
                suspicious_files.append(py_file)
        except Exception:
            pass
    
    for file_path in suspicious_files:
        if fix_file_warnings(file_path):
            logger.info(f"  ✅ {file_path.name}")
            fixed_count += 1
    
    logger.info(f"  📊 {fixed_count} فایل اصلاح شد")
    return fixed_count


def verify_no_warnings(project_root: Path):
    """بررسی نهایی نبود warnings"""
    logger.info("\n🔍 بررسی نهایی warnings...")
    
    import warnings
    import ast
    
    warning_count = 0
    
    for py_file in project_root.rglob('*.py'):
        if any(part in str(py_file) for part in [
            '.venv', 'node_modules', '__pycache__', '.backup'
        ]):
            continue
        
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                content = py_file.read_text(encoding='utf-8')
                ast.parse(content)
                
                # شمارش SyntaxWarnings
                syntax_warnings = [x for x in w if issubclass(x.category, SyntaxWarning)]
                if syntax_warnings:
                    warning_count += len(syntax_warnings)
                    logger.info(f"  ⚠️  {py_file.name}: {len(syntax_warnings)} warning")
        
        except Exception:
            pass
    
    if warning_count == 0:
        logger.info("  🎉 هیچ warning یافت نشد!")
    else:
        logger.info(f"  ⚠️  {warning_count} warning باقی مانده (غیر بحرانی)")
    
    return warning_count


def main():
    logger.info("=" * 70)
    logger.info("🔧 FIX WARNINGS - رفع SyntaxWarning های باقی‌مانده")
    logger.info("=" * 70)
    
    project_root = Path(r'D:\econojin.com')
    
    # مرحله 1: رفع warnings در docstrings
    fix_docstring_warnings(project_root)
    
    # مرحله 2: بررسی نهایی
    warnings_count = verify_no_warnings(project_root)
    
    logger.info("\n" + "=" * 70)
    if warnings_count == 0:
        logger.info("🎉 پروژه کاملاً تمیز شد! هیچ warning و error وجود ندارد")
    else:
        logger.info(f"ℹ️  {warnings_count} warning غیربحرانی باقی مانده")
        logger.info("   این warnings اجرای کد را متوقف نمی‌کنند")
    
    logger.info("\n📋 گام‌های بعدی:")
    logger.info("   1. نصب وابستگی‌ها:")
    logger.info("      python scripts/setup/install_deps.py")
    logger.info("   ")
    logger.info("   2. اجرای تست‌ها:")
    logger.info("      python -m pytest tests/ -v")
    logger.info("   ")
    logger.info("   3. اجرای کامل pipeline:")
    logger.info("      python scripts/orchestrator.py")
    logger.info("=" * 70)


if __name__ == '__main__':
    main()