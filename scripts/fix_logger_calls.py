#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
رفع خودکار همه تماس‌های logger که با ساختار structlog نوشته شده‌اند
و تبدیل آن‌ها به فرمت سازگار با logging استاندارد پایتون
r"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(r"D:\econojin.com")


def backup_file(file_path: Path) -> Path:
    """ایجاد backup قبل از تغییر"""
    backup_dir = file_path.parent / ".logger_fix_backup"
    backup_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{file_path.stem}_{ts}{file_path.suffix}"
    shutil.copy2(file_path, backup_path)
    return backup_path


def fix_logger_calls(file_path: Path) -> bool:
    """
    رفع تماس‌های logger.info/warning/error که از ساختار structlog استفاده می‌کنند

    الگوهای هدف:
        logger.info(f"message | key1={value1} | key2={value2}")

    تبدیل به:
        logger.info(f"message | key1={value1} | key2={value2}")
    r"""
    content = file_path.read_text(encoding="utf-8")
    original = content

    # الگوی regex برای پیدا کردن تماس‌های چندخطی logger
    # مثال: logger.info(\n    "msg",\n    key=value,\n)
    pattern = re.compile(
        r"(\s*)(logger\.(?:info|warning|error|debug|critical))\s*\(\s*\n"  # تورفتگی + logger.xxx(
        r'(\s*)["\']([^"\']+)["\']'  # "message"
        r"((?:\s*,\s*\n\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^,\n]+)*)"  # , key=value ها
        r"\s*,?\s*\n\s*\)",  # )
        re.MULTILINE,
    )

    def replace_logger_call(match):
        indent = match.group(1)  # تورفتگی خط logger
        logger_call = match.group(2)  # logger.info
        # msg_indent = match.group(3)    # تورفتگی message (لازم نیست)
        message = match.group(4)  # متن پیام
        kwargs_block = match.group(5)  # کل block key=value

        # استخراج جفت‌های key=value
        kv_pattern = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^,\n]+)")
        kv_pairs = kv_pattern.findall(kwargs_block)

        # ساخت پیام f-string
        if kv_pairs:
            kv_parts = [f"{k}={{{v.strip()}}}" for k, v in kv_pairs]
            full_message = f"{message} | " + " | ".join(kv_parts)
            return f'{indent}{logger_call}(f"{full_message}")'
        else:
            return f'{indent}{logger_call}("{message}")'

    # اعمال جایگزینی
    content = pattern.sub(replace_logger_call, content)

    # الگوی دوم: تماس‌های تک‌خطی با آرگومان‌های کلیدی
    # logger.info(f"msg | key={value}")
    pattern_single = re.compile(
        r"(\s*)(logger\.(?:info|warning|error|debug|critical))\s*\(\s*"
        r'["\']([^"\']+)["\']\s*'
        r"((?:,\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^,\)]+)+)"
        r"\s*\)"
    )

    def replace_single(match):
        indent = match.group(1)
        logger_call = match.group(2)
        message = match.group(3)
        kwargs = match.group(4)

        kv_pattern = re.compile(r",\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^,\)]+)")
        kv_pairs = kv_pattern.findall(kwargs)

        if kv_pairs:
            kv_parts = [f"{k}={{{v.strip()}}}" for k, v in kv_pairs]
            full_message = f"{message} | " + " | ".join(kv_parts)
            return f'{indent}{logger_call}(f"{full_message}")'
        return match.group(0)

    content = pattern_single.sub(replace_single, content)

    if content != original:
        backup_file(file_path)
        file_path.write_text(content, encoding="utf-8")
        return True
    return False


def main():
    print("=" * 70)
    print("🔧 LOGGER CALL FIXER - رفع خودکار تماس‌های logger")
    print("=" * 70)

    IGNORE = [
        ".venv",
        "node_modules",
        "__pycache__",
        ".backup",
        ".emergency_backup",
        ".syntax_backup",
        ".warnings_backup",
        ".final_backup",
        ".logger_fix_backup",
        "site-packages",
    ]

    fixed_files = []
    checked = 0

    for py_file in PROJECT_ROOT.rglob("*.py"):
        if any(p in str(py_file) for p in IGNORE):
            continue

        # رد کردن خود اسکریپت logger.py
        if py_file.name == "logger.py" and "core" in str(py_file):
            continue

        checked += 1
        try:
            if fix_logger_calls(py_file):
                fixed_files.append(py_file.relative_to(PROJECT_ROOT))
                print(f"  [OK] {py_file.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            print(f"  [WARN] {py_file.relative_to(PROJECT_ROOT)}: {e}")

    print("\n" + "-" * 70)
    print(f"📊 Checked: {checked} files")
    print(f"✅ Fixed: {len(fixed_files)} files")

    if fixed_files:
        print("\n📁 Files fixed:")
        for f in fixed_files:
            print(f"   - {f}")

    print("\n" + "=" * 70)
    print("🚀 Next: Run 'python test_gaia.py'")
    print("=" * 70)


if __name__ == "__main__":
    main()
