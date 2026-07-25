#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_config.py — بررسی و اصلاح FIRST_SUPERUSER_PASSWORD در config.py"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "apps" / "shared_core" / "config.py"


def main() -> int:
    if not CONFIG.exists():
        print(f"  ❌ یافت نشد: {CONFIG}")
        return 1

    text = CONFIG.read_text(encoding="utf-8")
    lines = text.splitlines()

    # ۱. نمایش خطوط مرتبط
    print("  📄 خطوط مرتبط با FIRST_SUPERUSER_PASSWORD:")
    found_lines = []
    for i, line in enumerate(lines, 1):
        if "SUPERUSER" in line.upper() or "FIRST_SUPER" in line:
            print(f"     خط {i}: {line.strip()}")
            found_lines.append(i)

    if not found_lines:
        print("  ⚪ هیچ ارجاعی یافت نشد")
        return 0

    # ۲. بررسی اینکه آیا هنوز default hardcoded دارد
    has_hardcoded = re.search(
        r'FIRST_SUPERUSER_PASSWORD[^#\n]*=\s*["\'][^"\']+["\']', text)
    if not has_hardcoded:
        print("\n  ✅ default hardcoded ندارد (قبلاً اصلاح شده یا از env می‌خواند)")
        return 0

    # ۳. تلاش برای اصلاح با الگوهای متعدد
    patterns = [
        # pydantic: FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "")  # SEC: from env
        (r'(FIRST_SUPERUSER_PASSWORD:\s*str\s*=\s*)["\'][^"\']*["\']',
         r'\1os.getenv("FIRST_SUPERUSER_PASSWORD", "")  # SEC: no hardcoded default'),
        # ساده: FIRST_SUPERUSER_PASSWORD = os.getenv("FIRST_SUPERUSER_PASSWORD", "")  # SEC: from env
        (r'(FIRST_SUPERUSER_PASSWORD\s*=\s*)["\'][^"\']*["\']',
         r'\1os.getenv("FIRST_SUPERUSER_PASSWORD", "")  # SEC: no hardcoded default'),
        # pydantic Field: Field(default="...") یا Field("...")
        (r'(FIRST_SUPERUSER_PASSWORD[^=\n]*=\s*Field\(\s*(?:default\s*=\s*)?)["\'][^"\']*["\']',
         r'\1os.getenv("FIRST_SUPERUSER_PASSWORD", "")'),
    ]

    new_text = text
    total = 0
    for pattern, repl in patterns:
        new_text, n = re.subn(pattern, repl, new_text)
        total += n

    if total == 0:
        print("\n  ⚠️  الگوی شناخته‌شده match نشد. خط را دستی بررسی کنید:")
        for i in found_lines:
            print(f"     خط {i}: {lines[i-1].strip()}")
        return 1

    # اطمینان از import os
    if "import os" not in new_text:
        new_text = "import os\n" + new_text

    CONFIG.write_text(new_text, encoding="utf-8")
    print(f"\n  ✅ اصلاح شد ({total} مورد) — default حذف و به env منتقل شد")
    print("  ⚠️  مطمئن شوید متغیر FIRST_SUPERUSER_PASSWORD در .env تنظیم است")
    return 0


if __name__ == "__main__":
    sys.exit(main())