import logging

logger = logging.getLogger(__name__)

#!/usr/bin/env python3
"""
رفع فوری خطاهای بحرانی پروژه
- Circular Import در safety.py
- SafeSubprocess برای Windows
- Syntax Error در farmer.py
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


def backup_file(file_path: Path) -> Path:
    """ایجاد backup قبل از تغییر"""
    backup_dir = file_path.parent / '.emergency_backup'
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
    shutil.copy2(file_path, backup_path)
    logger.info(f"  💾 Backup: {backup_path.name}")
    return backup_path


def fix_circular_import(project_root: Path):
    """رفع circular import در safety.py"""
    logger.info("\n🔧 رفع Circular Import در safety.py...")
    
    safety_file = project_root / 'scripts' / 'core' / 'safety.py'
    
    if not safety_file.exists():
        logger.info(f"  ❌ فایل یافت نشد: {safety_file}")
        return False
    
    backup_file(safety_file)
    
    content = safety_file.read_text(encoding='utf-8')
    original = content
    
    # حذف import های اشتباه که توسط fix_subprocess اضافه شده
    patterns_to_remove = [
        r'^from core\.safety import SafeSubprocess\s*\n',
        r'^from core\.safety import\s*\n',
        r'^from scripts\.core\.safety import SafeSubprocess\s*\n',
    ]
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    # حذف خطوط خالی اضافی در ابتدا
    content = re.sub(r'^\n{3,}', '\n\n', content)
    
    if content != original:
        safety_file.write_text(content, encoding='utf-8')
        logger.info(f"  ✅ Circular import رفع شد")
        return True
    else:
        logger.info(f"  ℹ️  نیازی به تغییر نبود")
        return False


def fix_safe_subprocess_windows(project_root: Path):
    """اصلاح SafeSubprocess برای پشتیبانی از Windows"""
    logger.info("\n🔧 اصلاح SafeSubprocess برای Windows...")
    
    safety_file = project_root / 'scripts' / 'core' / 'safety.py'
    
    if not safety_file.exists():
        logger.info(f"  ❌ فایل یافت نشد")
        return False
    
    backup_file(safety_file)
    
    content = safety_file.read_text(encoding='utf-8')
    
    # پیدا کردن و جایگزینی متد run در SafeSubprocess
    old_validation = '''        base_command = command[0]
        if base_command not in cls.ALLOWED_COMMANDS:
            raise ValueError(
                f"Command '{base_command}' not allowed. "
                f"Allowed: {cls.ALLOWED_COMMANDS}"
            )'''
    
    new_validation = '''        base_command = command[0]
        # استخراج نام دستور (بدون مسیر و extension) برای سازگاری با Windows
        from pathlib import Path as _Path
        try:
            cmd_name = _Path(base_command).stem.lower()
        except Exception:
            cmd_name = str(base_command).lower()
        
        # بررسی نام دستور در لیست مجاز
        allowed_lower = {c.lower() for c in cls.ALLOWED_COMMANDS}
        if cmd_name not in allowed_lower:
            raise ValueError(
                f"Command '{base_command}' (resolved: '{cmd_name}') not allowed. "
                f"Allowed: {cls.ALLOWED_COMMANDS}"
            )'''
    
    if old_validation in content:
        content = content.replace(old_validation, new_validation)
        safety_file.write_text(content, encoding='utf-8')
        logger.info(f"  ✅ SafeSubprocess برای Windows اصلاح شد")
        return True
    else:
        # تلاش برای جایگزینی الگوی دیگر
        logger.info(f"  ⚠️  الگوی مورد انتظار یافت نشد. بررسی دستی لازم است.")
        return False


def fix_farmer_syntax(project_root: Path):
    """رفع Syntax Error در farmer.py"""
    logger.info("\n🔧 رفع Syntax Error در farmer.py...")
    
    farmer_file = project_root / 'scripts' / 'api' / 'routers' / 'farmer.py'
    
    if not farmer_file.exists():
        logger.info(f"  ❌ فایل یافت نشد: {farmer_file}")
        return False
    
    backup_file(farmer_file)
    
    content = farmer_file.read_text(encoding='utf-8')
    original = content
    
    # رفع مشکلات رایج ایجاد شده توسط print_to_logging
    fixes = [
        # اگر logger بدون import استفاده شده
        (r'(?<!\w)logger\.', 'logger.'),
        
        # رفع خطوطی که logger در آن‌ها تعریف نشده
        # اضافه کردن import در ابتدای فایل اگر لازم باشد
    ]
    
    # بررسی نیاز به import logger
    if 'logger.' in content and 'UnifiedLogger' not in content:
        # اضافه کردن import در بالای فایل
        import_block = '''from scripts.core.logger import UnifiedLogger
logger = UnifiedLogger.get_logger(__name__)

r'''
        # پیدا کردن اولین خط بعد از docstring و imports
        lines = content.split('\n')
        insert_idx = 0
        
        for i, line in enumerate(lines):
            if line.startswith('r"""') or line.startswith("'''"):
                # پیدا کردن پایان docstring
                quote = line[:3]
                if line.count(quote) == 1:
                    # docstring چند خطی
                    for j in range(i+1, len(lines)):
                        if quote in lines[j]:
                            insert_idx = j + 1
                            break
                else:
                    insert_idx = i + 1
            elif line.startswith('import') or line.startswith('from'):
                insert_idx = i + 1
            elif line.strip() and insert_idx > 0:
                break
        
        lines.insert(insert_idx, import_block)
        content = '\n'.join(lines)
    
    if content != original:
        farmer_file.write_text(content, encoding='utf-8')
        logger.info(f"  ✅ farmer.py رفع شد")
        return True
    else:
        logger.info(f"  ℹ️  نیازی به تغییر نبود")
        return False


def fix_install_deps_python_path(project_root: Path):
    """رفع مشکل sys.executable در install_deps.py"""
    logger.info("\n🔧 رفع مشکل sys.executable در install_deps.py...")
    
    install_file = project_root / 'scripts' / 'setup' / 'install_deps.py'
    
    if not install_file.exists():
        logger.info(f"  ❌ فایل یافت نشد")
        return False
    
    backup_file(install_file)
    
    content = install_file.read_text(encoding='utf-8')
    
    # جایگزینی sys.executable با 'python' برای سازگاری با SafeSubprocess
    # در upgrade_pip
    old_code = '''SafeSubprocess.run([
                sys.executable, '-m', 'pip', 'install',
                '--upgrade', 'pip', 'setuptools', 'wheel'
            ])'''
    
    new_code = '''SafeSubprocess.run([
                'python', '-m', 'pip', 'install',
                '--upgrade', 'pip', 'setuptools', 'wheel'
            ])'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
    
    # همچنین create_virtualenv
    old_venv = '''SafeSubprocess.run([
                sys.executable, '-m', 'venv',
                '--clear',
                str(self.venv_path)
            ])'''
    
    new_venv = '''SafeSubprocess.run([
                'python', '-m', 'venv',
                '--clear',
                str(self.venv_path)
            ])'''
    
    if old_venv in content:
        content = content.replace(old_venv, new_venv)
    
    install_file.write_text(content, encoding='utf-8')
    logger.info(f"  ✅ install_deps.py اصلاح شد")
    return True


def verify_syntax(file_path: Path) -> bool:
    """بررسی syntax یک فایل"""
    import ast
    try:
        content = file_path.read_text(encoding='utf-8')
        ast.parse(content)
        return True
    except SyntaxError as e:
        logger.info(f"  ❌ SyntaxError در {file_path.name}: {e}")
        return False


def verify_all_python_files(project_root: Path):
    """بررسی syntax همه فایل‌های پایتون"""
    logger.info("\n🔍 بررسی Syntax همه فایل‌های پایتون...")
    
    errors = []
    checked = 0
    
    for py_file in project_root.rglob('*.py'):
        # نادیده گرفتن backup و venv
        if any(part in str(py_file) for part in [
            '.venv', 'node_modules', '__pycache__',
            '.backup', '.emergency_backup'
        ]):
            continue
        
        checked += 1
        if not verify_syntax(py_file):
            errors.append(py_file)
    
    logger.info(f"  📊 بررسی شد: {checked} فایل")
    logger.info(f"  ✅ سالم: {checked - len(errors)} فایل")
    logger.info(f"  ❌ خطا: {len(errors)} فایل")
    
    if errors:
        logger.info(f"\n  فایل‌های دارای خطا:")
        for e in errors[:10]:  # فقط 10 تا اول
            logger.info(f"    - {e.relative_to(project_root)}")
    
    return errors


def main():
    print("=" * 70)
    logger.info("🚨 EMERGENCY FIX - رفع خطاهای بحرانی")
    print("=" * 70)
    
    project_root = Path(r'D:\\econojin.com')
    
    # مرحله 1: رفع circular import
    fix_circular_import(project_root)
    
    # مرحله 2: اصلاح SafeSubprocess
    fix_safe_subprocess_windows(project_root)
    
    # مرحله 3: رفع farmer.py
    fix_farmer_syntax(project_root)
    
    # مرحله 4: رفع install_deps.py
    fix_install_deps_python_path(project_root)
    
    # مرحله 5: بررسی syntax همه فایل‌ها
    errors = verify_all_python_files(project_root)
    
    print("\n" + "=" * 70)
    if errors:
        logger.info(f"⚠️  {len(errors)} فایل هنوز دارای Syntax Error هستند")
        logger.info("💡 پیشنهاد: این فایل‌ها را دستی بررسی کنید")
    else:
        logger.info("🎉 همه فایل‌ها از نظر syntax سالم هستند!")
    
    logger.info("\n📋 گام‌های بعدی:")
    logger.info("   1. اجرای مجدد orchestrator:")
    logger.info("      python scripts/orchestrator.py")
    logger.info("\n   2. یا اجرای دستی هر مرحله:")
    logger.info("      python scripts/security/fix_exec.py")
    logger.info("      python scripts/security/fix_subprocess.py")
    logger.info("      python scripts/setup/install_deps.py")
    print("=" * 70)


if __name__ == '__main__':
    main()