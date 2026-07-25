#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_configs.py — بررسی و اصلاح فایل‌های config
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
خطوط حاوی PASSWORD/SECRET را نمایش و defaultهای hardcoded را اصلاح می‌کند.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG_FILES = [
    "apps/shared_core/config.py",
    "apps/users/config.py",
]

# الگوهای اصلاح (فقط defaultهای hardcoded را هدف می‌گیرند)
FIX_PATTERNS = [
    (r'(FIRST_SUPERUSER_PASSWORD:\s*str\s*=\s*)["\'][^"\']+["\']',
     r'\1os.getenv("FIRST_SUPERUSER_PASSWORD", "")  # SEC: from env'),
    (r'(SECRET_KEY:\s*str\s*=\s*)["\'][^"\']+["\']',
     r'\1os.getenv("SECRET_KEY", "")  # SEC: from env'),
    (r'(JWT_SECRET:\s*str\s*=\s*)["\'][^"\']+["\']',
     r'\1os.getenv("JWT_SECRET_KEY", "")  # SEC: from env'),
    (r'(DATABASE_URL:\s*str\s*=\s*)["\']postgresql://[^"\']+["\']',
     r'\1os.getenv("DATABASE_URL", "")  # SEC: from env'),
    (r'(API_KEY:\s*str\s*=\s*)["\'][^"\']+["\']',
     r'\1os.getenv("API_KEY", "")  # SEC: from env'),
]

SENSITIVE_KEYWORDS = ["PASSWORD", "SECRET", "API_KEY", "TOKEN", "DATABASE_URL"]


def main() -> int:
    apply = "--apply" in sys.argv
    print("═" * 60)
    print("  🔍 بررسی فایل‌های config")
    print("═" * 60)
    if not apply:
        print("  ℹ️  حالت گزارش — برای اعمال: --apply")

    total_fixed = 0
    for rel in CONFIG_FILES:
        f = ROOT / rel
        if not f.exists():
            print(f"\n  ⚪ {rel} — یافت نشد")
            continue

        text = f.read_text(encoding="utf-8")
        lines = text.splitlines()

        print(f"\n  📄 {rel}")
        print("  ─" * 25)

        # نمایش خطوط حساس
        found_sensitive = False
        for i, line in enumerate(lines, 1):
            if any(k in line.upper() for k in SENSITIVE_KEYWORDS):
                found_sensitive = True
                # mask کردن مقادیر در نمایش
                display = re.sub(r'(["\'])([^"\']{4})[^"\']*(["\'])',
                                 r'\1\2…\3', line.strip())
                print(f"     خط {i}: {display}")

        if not found_sensitive:
            print("     ✅ هیچ متغیر حساسی یافت نشد")
            continue

        # بررسی default hardcoded
        has_hardcoded = re.search(
            r'(PASSWORD|SECRET|API_KEY|DATABASE_URL)[^#\n]*=\s*["\'][^"\']+["\']',
            text)
        if not has_hardcoded:
            print("     ✅ default hardcoded ندارد (از env می‌خواند)")
            continue

        # اصلاح
        new_text = text
        fixed = 0
        for pattern, repl in FIX_PATTERNS:
            new_text, n = re.subn(pattern, repl, new_text)
            fixed += n

        if fixed == 0:
            print("     ⚠️  الگوی شناخته‌شده match نشد — دستی بررسی کنید")
            continue

        if "import os" not in new_text:
            new_text = "import os\n" + new_text

        print(f"     🔧 {fixed} default hardcoded یافت شد")
        if apply:
            f.write_text(new_text, encoding="utf-8")
            print(f"     ✅ اصلاح شد (به env منتقل شد)")
            total_fixed += fixed
        else:
            print(f"     → با --apply اصلاح می‌شود")

    print("\n" + "═" * 60)
    if apply:
        print(f"  ✅ مجموعاً {total_fixed} مورد اصلاح شد")
    else:
        print("  → برای اعمال: python check_configs.py --apply")
    print("═" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())