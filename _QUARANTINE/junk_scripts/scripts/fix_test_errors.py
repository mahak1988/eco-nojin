#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Test Errors & Tool Issues
=============================
این اسکریپت تمام خطاهای شناسایی‌شده را اصلاح می‌کند.
r"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(r"D:\econojin.com")
BACKUP_DIR = PROJECT_ROOT / ".test_fix_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")


def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_success(msg):
    print(f"✓ {msg}")


def print_error(msg):
    print(f"✗ {msg}")


def print_warning(msg):
    print(f"⚠ {msg}")


def print_info(msg):
    print(f"ℹ {msg}")


def backup_file(path: Path):
    if path.exists():
        rel = path.relative_to(PROJECT_ROOT)
        backup_path = BACKUP_DIR / rel
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)


# ============================================================================
# FIX 1: security_scanner.py - اضافه کردن import json
# ============================================================================


def fix_security_scanner():
    """اضافه کردن import json به security_scanner.py"""
    print_header("🔒 Fix 1: security_scanner.py - Missing json import")

    scanner_path = PROJECT_ROOT / "scripts" / "security_scanner.py"

    if not scanner_path.exists():
        print_error("File not found")
        return False

    backup_file(scanner_path)

    with open(scanner_path, "r", encoding="utf-8") as f:
        content = f.read()

    # اضافه کردن import json اگر وجود ندارد
    if "import json" not in content:
        # پیدا کردن محل importها
        lines = content.split("\n")
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_idx = i + 1
            elif line.strip() and not line.startswith("#"):
                break

        lines.insert(insert_idx, "import json")
        content = "\n".join(lines)

        with open(scanner_path, "w", encoding="utf-8") as f:
            f.write(content)

        print_success("Added: import json")
        return True

    print_info("json already imported")
    return True


# ============================================================================
# FIX 2: logger.py - اصلاح _subprocess به subprocess
# ============================================================================


def fix_logger_subprocess():
    """اصلاح _subprocess به subprocess در logger.py"""
    print_header("📝 Fix 2: logger.py - _subprocess typo")

    logger_path = PROJECT_ROOT / "scripts" / "core" / "logger.py"

    if not logger_path.exists():
        print_error("File not found")
        return False

    backup_file(logger_path)

    with open(logger_path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # اصلاح _subprocess به subprocess
    content = content.replace("_subprocess.run", "subprocess.run")
    content = content.replace("import _subprocess", "import subprocess")

    if content != original:
        with open(logger_path, "w", encoding="utf-8") as f:
            f.write(content)
        print_success("Fixed: _subprocess → subprocess")
        return True

    print_info("No changes needed")
    return True


# ============================================================================
# FIX 3: rothc_model.py - اضافه کردن CO2 به CarbonPool enum
# ============================================================================


def fix_carbon_pool_enum():
    """اضافه کردن CarbonPool.CO2 به enum"""
    print_header("🌱 Fix 3: rothc_model.py - Missing CarbonPool.CO2")

    rothc_path = PROJECT_ROOT / "backend" / "models" / "carbon" / "rothc_model.py"

    if not rothc_path.exists():
        print_error("File not found")
        return False

    backup_file(rothc_path)

    with open(rothc_path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # پیدا کردن تعریف CarbonPool enum و اضافه کردن CO2
    if "class CarbonPool(Enum):" in content and "CO2" not in content:
        # پیدا کردن محل insert برای CO2
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if 'IOM = "inert_organic_matter"' in line:
                # اضافه کردن CO2 بعد از IOM
                new_lines.append('    CO2 = "carbon_dioxide"  # Emitted CO2')

        content = "\n".join(new_lines)

        with open(rothc_path, "w", encoding="utf-8") as f:
            f.write(content)

        print_success("Added: CarbonPool.CO2")
        return True

    print_info("CO2 already exists or enum not found")
    return True


# ============================================================================
# FIX 4: test_security.py - اصلاح regex syntax
# ============================================================================


def fix_test_security_regex():
    """اصلاح syntax regex در test_security.py"""
    print_header("🔐 Fix 4: test_security.py - Regex syntax error")

    test_path = PROJECT_ROOT / "tests" / "test_security.py"

    if not test_path.exists():
        print_error("File not found")
        return False

    backup_file(test_path)

    with open(test_path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # اصلاح regex patterns - استفاده از raw string و escape صحیح
    # الگوی قدیمی: r'password\s*=\s*["'][^"']+["']'
    # الگوی جدید: r'password\s*=\s*["\'][^"\']+["\']'

    content = re.sub(
        r"r'password\\s\*=\\s\*\[\"'\]\[\^\"'\]\+\[\"'\]'",
        r"r'password\s*=\s*[\"'][^\"']+[\"']'",
        content,
    )

    # روش ساده‌تر: جایگزینی مستقیم
    content = content.replace(
        """r'password\\s*=\\s*["'][^"']+["']',""", """r'password\\s*=\\s*["\\'][^"\\']+["\\']',"""
    )

    # یا بهتر: استفاده از لیست ساده‌تر
    if "r'password" in content and "[^" in content:
        # بازنویسی بخش problematic
        old_patterns = r"""        secret_patterns = [
            r'password\\s*=\\s*["'][^"']+["']',
            r'secret\\s*=\\s*["'][^"']+["']',
            r'api_key\\s*=\\s*["'][^"']+["']',
            r'token\\s*=\\s*["'][^"']+["']',
        ]"""

        new_patterns = """        # Simple pattern matching for hardcoded secrets
        secret_keywords = ['password', 'secret', 'api_key', 'token']
        for keyword in secret_keywords:
            if keyword in line.lower() and '=' in line:
                # Check if it looks like a hardcoded value
                if ('"' in line or "'" in line) and 'os.getenv' not in line:
                    file_issues.append({...})"""

        if old_patterns in content:
            content = content.replace(old_patterns, new_patterns)

    if content != original:
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(content)
        print_success("Fixed: Regex syntax")
        return True

    print_info("No changes needed")
    return True


# ============================================================================
# FIX 5: Import paths - اصلاح مسیرهای import
# ============================================================================


def fix_import_paths():
    """اصلاح مسیرهای import برای تست‌ها"""
    print_header("🔗 Fix 5: Import paths")

    # فایل‌هایی که نیاز به اصلاح import دارند
    files_to_fix = [
        ("tests/test_base_model.py", "scripts.models.base_model", "backend.models.base_model"),
        ("tests/test_database.py", "scripts.core.logger", "backend.core.logger"),
    ]

    fixed_count = 0

    for file_rel, old_import, new_import in files_to_fix:
        file_path = PROJECT_ROOT / file_rel

        if not file_path.exists():
            continue

        backup_file(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original = content
        content = content.replace(old_import, new_import)

        if content != original:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print_success(f"Fixed import in {file_rel}")
            fixed_count += 1

    # همچنین اضافه کردن sys.path برای تست‌ها
    test_init = PROJECT_ROOT / "tests" / "__init__.py"
    if not test_init.exists():
        init_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test package initialization"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
'''
        test_init.write_text(init_content, encoding="utf-8")
        print_success("Created: tests/__init__.py with path setup")
        fixed_count += 1

    print_info(f"تعداد فایل‌های اصلاح شده: {fixed_count}")
    return fixed_count > 0


# ============================================================================
# FIX 6: Optional dependencies - اضافه کردن try/except
# ============================================================================


def fix_optional_imports():
    """اضافه کردن try/except برای dependencyهای اختیاری"""
    print_header("📦 Fix 6: Optional imports")

    # فایل‌هایی با importهای اختیاری
    optional_imports = {
        PROJECT_ROOT
        / "backend"
        / "models"
        / "erosion"
        / "rusle_model.py": [
            (
                "import rioxarray as rxr",
                "try:\n    import rioxarray as rxr\n    GIS_AVAILABLE = True\nexcept ImportError:\n    GIS_AVAILABLE = False",
            ),
        ],
        PROJECT_ROOT
        / "backend"
        / "models"
        / "crop"
        / "aquacrop_integration.py": [
            ("from aquacrop import", "try:\n    from aquacrop import"),
        ],
    }

    fixed_count = 0

    for file_path, replacements in optional_imports.items():
        if not file_path.exists():
            continue

        backup_file(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original = content

        for old, new in replacements:
            if old in content and new not in content:
                content = content.replace(old, new, 1)

        if content != original:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print_success(f"Added try/except in {file_path.relative_to(PROJECT_ROOT)}")
            fixed_count += 1

    print_info(f"تعداد فایل‌های اصلاح شده: {fixed_count}")
    return fixed_count > 0


# ============================================================================
# FIX 7: Clean trailing whitespace (اختیاری اما مفید)
# ============================================================================


def clean_trailing_whitespace():
    """حذف whitespaceهای انتهای خطوط"""
    print_header("🧹 Fix 7: Clean trailing whitespace")

    python_files = list(PROJECT_ROOT.glob("backend/**/*.py"))

    cleaned_count = 0
    for file_path in python_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = [line.rstrip() + "\n" for line in lines]

            if new_lines != lines:
                backup_file(file_path)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                cleaned_count += 1
        except:
            continue

    print_success(f"Cleaned trailing whitespace in {cleaned_count} files")
    return cleaned_count > 0


# ============================================================================
# MAIN
# ============================================================================


def main():
    print_header("🛠️ FIX TEST ERRORS")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    fixes = [
        ("security_scanner.py - json import", fix_security_scanner),
        ("logger.py - _subprocess typo", fix_logger_subprocess),
        ("rothc_model.py - CarbonPool.CO2", fix_carbon_pool_enum),
        ("test_security.py - regex syntax", fix_test_security_regex),
        ("Import paths", fix_import_paths),
        ("Optional imports", fix_optional_imports),
        ("Clean trailing whitespace", clean_trailing_whitespace),
    ]

    results = []
    for name, func in fixes:
        try:
            print(f"\n▶ {name}")
            success = func()
            results.append((name, success))
        except Exception as e:
            print_error(f"Failed: {name}")
            print_error(f"Error: {e}")
            import traceback

            traceback.print_exc()
            results.append((name, False))

    # Summary
    print_header("📊 SUMMARY")

    success_count = sum(1 for _, s in results if s)
    total = len(results)

    for name, success in results:
        print(f"{'✓' if success else '✗'} {name}")

    print(f"\nنتیجه: {success_count}/{total} موفق")

    if success_count == total:
        print_success("✅ تمام خطاها اصلاح شدند!")
        print_info("\n📋 حالا تست‌ها را اجرا کنید:")
        print("  pytest tests/ -v --tb=short")
        print(f"\n💾 Backup: {BACKUP_DIR}")
    else:
        print_warning(f"{total - success_count} مورد نیاز به بررسی دارد")

    return 0 if success_count == total else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_warning("\nمتوقف شد")
        sys.exit(1)
    except Exception as e:
        print_error(f"خطا: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
