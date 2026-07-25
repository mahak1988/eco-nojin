#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_config_defaults.py — حذف defaultهای hardcoded از config.py (فرمت pydantic Field)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "apps" / "shared_core" / "config.py"


def main() -> int:
    apply = "--apply" in sys.argv

    if not CONFIG.exists():
        print(f"  ❌ یافت نشد: {CONFIG}")
        return 1

    text = CONFIG.read_text(encoding="utf-8")

    print("═" * 60)
    print("  🔧 حذف defaultهای hardcoded از config.py")
    print("═" * 60)
    if not apply:
        print("  ℹ️  حالت گزارش — برای اعمال: --apply")

    # نمایش وضعیت فعلی
    for i, line in enumerate(text.splitlines(), 1):
        if "Field(default=" in line and any(
                k in line for k in ("DATABASE_URL", "SECRET_KEY")):
            display = re.sub(r'(["\'])([^"\']{4})[^"\']*(["\'])',
                             r'\1\2…\3', line.strip())
            print(f"  📌 خط {i}: {display}")

    # الگوهای اصلاح: حذف default از Field برای متغیرهای حساس
    # Field(default="...", description="...") → Field(..., description="...")
    patterns = [
        (r'(DATABASE_URL:\s*str\s*=\s*Field\(\s*)default\s*=\s*["\'][^"\']*["\']\s*,\s*',
         r'\1..., '),
        (r'(SECRET_KEY:\s*str\s*=\s*Field\(\s*)default\s*=\s*["\'][^"\']*["\']\s*,\s*',
         r'\1..., '),
        # حالت بدون کاما (اگر default آخرین آرگومان باشد)
        (r'(DATABASE_URL:\s*str\s*=\s*Field\(\s*)default\s*=\s*["\'][^"\']*["\']\s*(\))',
         r'\1...\2'),
        (r'(SECRET_KEY:\s*str\s*=\s*Field\(\s*)default\s*=\s*["\'][^"\']*["\']\s*(\))',
         r'\1...\2'),
    ]

    new_text = text
    total = 0
    for pat, repl in patterns:
        new_text, n = re.subn(pat, repl, new_text)
        total += n

    if total == 0:
        print("\n  ⚠️  الگو match نشد — محتوای خطوط را بررسی کنید")
        return 1

    print(f"\n  🔧 {total} default hardcoded یافت شد")

    if apply:
        CONFIG.write_text(new_text, encoding="utf-8")
        print("  ✅ حذف شدند — pydantic اکنون از env می‌خواند")
        print("\n  ⚠️  مهم: مطمئن شوید این متغیرها در .env تنظیم‌اند:")
        print("     DATABASE_URL=postgresql://...")
        print("     SECRET_KEY=***")
        print("  در غیر این صورت اپلیکیشن هنگام شروع خطا می‌دهد (fail-safe)")
    else:
        print("  → برای اعمال: python fix_config_defaults.py --apply")

    return 0


if __name__ == "__main__":
    sys.exit(main())