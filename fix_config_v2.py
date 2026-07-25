#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_config_v2.py — حذف defaultهای hardcoded (رویکرد خط‌به‌خط، قوی‌تر)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "apps" / "shared_core" / "config.py"
SENSITIVE_KEYS = ["DATABASE_URL", "SECRET_KEY", "JWT_SECRET",
                  "LLM_API_KEY", "FAO_API_KEY", "PASSWORD"]


def main() -> int:
    if not CONFIG.exists():
        print(f"  ❌ یافت نشد: {CONFIG}")
        return 1

    apply = "--apply" in sys.argv
    text = CONFIG.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    print("═" * 60)
    print("  🔧 حذف defaultهای hardcoded (نسخه ۲)")
    print("═" * 60)
    if not apply:
        print("  ℹ️  حالت پیش‌نمایش — برای اعمال: --apply")

    # ۱. نمایش خطوط حساس (mask‌شده)
    print("\n  📄 خطوط حساس فعلی:")
    for i, line in enumerate(lines, 1):
        if any(k in line for k in SENSITIVE_KEYS) and ("Field(" in line or "=" in line):
            display = re.sub(r'(default\s*=\s*["\'])([^"\']{3})[^"\']*(["\'])',
                             r'\1\2…\3', line.rstrip())
            display = re.sub(r'(["\'])(postgresql|sqlite|mysql)([^"\']{3})[^"\']*(["\'])',
                             r'\1\2…\4', display)
            print(f"     خط {i}: {display.strip()}")

    # ۲. اصلاح خط‌به‌خط
    new_lines = []
    changed = []
    for i, line in enumerate(lines, 1):
        original = line
        if ("Field(" in line and "default" in line
                and any(k in line for k in SENSITIVE_KEYS)):
            # حذف default="..." یا default='...'
            line = re.sub(r'default\s*=\s*["\'][^"\']*["\']\s*,?\s*', '', line)
            # Field() خالی → Field(...)
            line = re.sub(r'Field\(\s*\)', 'Field(...)', line)
            # Field( , → Field(...,
            line = re.sub(r'Field\(\s*,\s*', 'Field(..., ', line)
            if line != original:
                changed.append((i, original.rstrip(), line.rstrip()))
        new_lines.append(line)

    if not changed:
        print("\n  ⚠️  هیچ default hardcoded یافت نشد")
        print("\n  🔍 محتوای کامل خطوط حساس (برای بررسی دستی):")
        for i, line in enumerate(lines, 1):
            if any(k in line for k in SENSITIVE_KEYS):
                print(f"     خط {i}: {line.rstrip()}")
        return 0

    # ۳. پیش‌نمایش تغییرات
    print(f"\n  🔧 {len(changed)} خط اصلاح خواهد شد:")
    for lineno, old, new in changed:
        print(f"\n     خط {lineno}:")
        print(f"       ❌ {old.strip()}")
        print(f"       ✅ {new.strip()}")

    if apply:
        CONFIG.write_text("".join(new_lines), encoding="utf-8")
        print(f"\n  ✅ {len(changed)} مورد اعمال شد")
        print("\n  ⚠️  مطمئن شوید این متغیرها در .env تنظیم‌اند:")
        print("     DATABASE_URL=postgresql://…word@host:5432/db")
        print("     SECRET_KEY=***")
    else:
        print("\n  → برای اعمال: python fix_config_v2.py --apply")

    return 0


if __name__ == "__main__":
    sys.exit(main())