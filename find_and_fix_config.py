#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
find_and_fix_config.py — جستجو و اصلاح FIRST_SUPERUSER_PASSWORD در کل پروژه
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKIP_DIRS = {".git", "node_modules", ".pnpm-store", "__pycache__",
             ".venv", "venv", ".security_backup", ".sync_backup_20260724_060347"}


def main() -> int:
    print("═" * 60)
    print("  🔍 جستجوی FIRST_SUPERUSER_PASSWORD در کل پروژه")
    print("═" * 60)

    found_files: list[Path] = []
    for py_file in ROOT.rglob("*.py"):
        if any(part in SKIP_DIRS or part.startswith(".sync_backup")
               for part in py_file.parts):
            continue
        try:
            text = py_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "FIRST_SUPERUSER" in text or "SUPERUSER_PASSWORD" in text:
            found_files.append(py_file)
            print(f"\n  📄 {py_file.relative_to(ROOT)}")
            for i, line in enumerate(text.splitlines(), 1):
                if "SUPERUSER" in line.upper():
                    print(f"     خط {i}: {line.strip()}")

    # بررسی .env
    env_file = ROOT / ".env"
    env_has_it = False
    if env_file.exists():
        env_text = env_file.read_text(encoding="utf-8", errors="ignore")
        if "FIRST_SUPERUSER" in env_text:
            env_has_it = True
            print(f"\n  ✅ در .env یافت شد (از env خوانده می‌شود — امن است)")

    if not found_files:
        print("\n  ⚪ هیچ فایل پایتونی حاوی FIRST_SUPERUSER_PASSWORD یافت نشد")
        if env_has_it:
            print("  ✅ متغیر در .env تعریف شده — وضعیت امن است")
        else:
            print("  → احتمالاً قبلاً حذف شده یا هرگز وجود نداشته")
        return 0

    # اصلاح فایل‌های یافت‌شده
    print(f"\n  🔧 اصلاح {len(found_files)} فایل …")
    patterns = [
        (r'(FIRST_SUPERUSER_PASSWORD:\s*str\s*=\s*)["\'][^"\']*["\']',
         r'\1os.getenv("FIRST_SUPERUSER_PASSWORD", "")  # SEC: from env'),
        (r'(FIRST_SUPERUSER_PASSWORD\s*=\s*)["\'][^"\']*["\']',
         r'\1os.getenv("FIRST_SUPERUSER_PASSWORD", "")  # SEC: from env'),
        (r'(FIRST_SUPERUSER_PASSWORD[^=\n]*=\s*Field\(\s*(?:default\s*=\s*)?)["\'][^"\']*["\']',
         r'\1os.getenv("FIRST_SUPERUSER_PASSWORD", "")'),
    ]
    for f in found_files:
        text = f.read_text(encoding="utf-8")
        new_text = text
        changed = False
        for pat, repl in patterns:
            new_text, n = re.subn(pat, repl, new_text)
            if n:
                changed = True
        if changed:
            if "import os" not in new_text:
                new_text = "import os\n" + new_text
            f.write_text(new_text, encoding="utf-8")
            print(f"  ✅ اصلاح شد: {f.relative_to(ROOT)}")
        else:
            print(f"  ⚠️  الگو match نشد: {f.relative_to(ROOT)}")
            print("     → محتوای خط را دستی بررسی کنید")
    return 0


if __name__ == "__main__":
    sys.exit(main())