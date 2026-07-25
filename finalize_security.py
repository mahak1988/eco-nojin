import os
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
finalize_security.py — مرحله نهایی ایمن‌سازی پروژه econojin
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
۱. پاکسازی فایل‌های موقت (replacements.txt، گزارش‌های guardian)
۲. patch امن فایل‌های واقعی (docker-compose، workflowها، READMEها)
۳. گزارش اقدامات دستی باقی‌مانده

استفاده:
  python finalize_security.py            # فقط گزارش
  python finalize_security.py --apply    # اعمال تغییرات
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# فایل‌های موقت/حساس که باید فیزیکاً حذف شوند
TEMP_FILES = ["replacements.txt"]
TEMP_GLOBS = ["reports/guardian_*.md", ".git_backup"]

# patchهای امن — فقط الگوهای مشخص رمز hardcode را هدف می‌گیرند
PATCHES = [
    ("docker-compose.prod.yml",
     "رمز DB production → ${DATABASE_URL}",
     r'(-\s*DATABASE_URL=)postgresql://[^@\s"\']+@[^\s"\']+',
     r'\1${DATABASE_URL}'),
    (".github/workflows/01-ci-main.yml",
     "رمز DB در CI → GitHub Secret",
     r'(DATABASE_URL:\s*)["\']?postgresql://[^\s"\']+["\']?',
     r'\1${{ secrets.DATABASE_URL }}'),
    (".github/workflows/05-deploy-production.yml",
     "رمز DB در deploy → GitHub Secret",
     r'(DATABASE_URL:\s*)["\']?postgresql://[^\s"\']+["\']?',
     r'\1${{ secrets.DATABASE_URL }}'),
    ("apps/cms/README.md",
     "mask رمز در مستندات CMS",
     r'(postgresql://[^:/\s"\']+:)[^@\s"\']+(@)',
     r'\1*****\2'),
    ("apps/users/README.md",
     "mask رمز در مستندات users",
     r'("password":\s*")[^"]{4,}(")',
     r'\1*****\2'),
    ("apps/admin_panel/README.md",
     "mask رمز در مستندات admin",
     r'("password":\s*")[^"]{4,}(")',
     r'\1*****\2'),
]


def step(num: str, title: str) -> None:
    print(f"\n{'─' * 60}\n  [{num}] {title}\n{'─' * 60}")


def cleanup_temp(apply: bool) -> None:
    step("۱", "پاکسازی فایل‌های موقت و گزارش‌های حساس")
    targets: list[Path] = []
    for name in TEMP_FILES:
        p = ROOT / name
        if p.exists():
            targets.append(p)
    for pattern in TEMP_GLOBS:
        targets.extend(ROOT.glob(pattern))

    if not targets:
        print("  ✅ هیچ فایل موقتی یافت نشد")
        return
    for p in targets:
        print(f"  ⚠️  {p.relative_to(ROOT)}")
    if apply:
        for p in targets:
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            else:
                p.unlink(missing_ok=True)
        print(f"  🗑️  {len(targets)} مورد حذف شد")


def apply_patches(apply: bool) -> None:
    step("۲", "patch امن فایل‌های واقعی (حذف رمز hardcode)")
    backup_dir = ROOT / ".security_backup"
    patched = 0
    for rel, desc, pattern, repl in PATCHES:
        path = ROOT / rel
        if not path.exists():
            print(f"  ⚪ {rel} — یافت نشد")
            continue
        text = path.read_text(encoding="utf-8")
        new_text, n = re.subn(pattern, repl, text)
        if n == 0:
            print(f"  ✅ {rel} — قبلاً اصلاح شده یا الگو یافت نشد")
            continue
        print(f"  🔧 {rel} — {desc} ({n} مورد)")
        if apply:
            backup_dir.mkdir(exist_ok=True)
            shutil.copy2(path, backup_dir / (rel.replace("/", "_") + ".bak"))
            path.write_text(new_text, encoding="utf-8")
            patched += 1
    if apply and patched:
        print(f"\n  💾 backupها در: {backup_dir.name}/")


def manual_actions() -> None:
    step("۳", "اقدامات دستی باقی‌مانده")
    print("""
  🔴 ضروری (امنیت production):

     ۱. apps/shared_core/config.py:137 — حذف default password:
        ┌─────────────────────────────────────────────────────────┐
        │ # قبل:                                                  │
        │ FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "")  # SEC: from env              │
        │ # بعد (pydantic از env می‌خواند):                       │
        │ FIRST_SUPERUSER_PASSWORD: str                           │
        └─────────────────────────────────────────────────────────┘

     ۲. ROTATE کردن همه رمزها (حتی پس از پاکسازی کد):
        • رمز DB production و test
        • QDRANT_API_KEY (.env:17)
        • FIRST_SUPERUSER_PASSWORD

     ۳. تنظیم GitHub Secrets (برای workflowها):
        GitHub → Settings → Secrets and variables → Actions → New
          نام: DATABASE_URL
          مقدار: postgresql://user:****@host:5432/db

  🟡 کم‌اهمیت (رمزهای ساختگی تست):
     • apps/conftest.py و apps/*/tests/test_*.py
     • واقعی نیستند؛ می‌توانید نادیده بگیرید یا به یک fixture مشترک منتقل کنید

  ⚪ مثبت کاذب i18n (اختیاری — حذف از گزارش):
     • apps/web/src/i18n/locales/*.json → کلید ترجمه "auth.password"
     • برای حذف، patch زیر را در project_analyzer.py اعمال کنید
""")


def main() -> int:
    p = argparse.ArgumentParser(description="مرحله نهایی ایمن‌سازی")
    p.add_argument("--apply", action="store_true", help="اعمال تغییرات")
    args = p.parse_args()

    print("═" * 60)
    print("  🔐 مرحله نهایی ایمن‌سازی — econojin.com")
    print("═" * 60)
    if not args.apply:
        print("  ℹ️  حالت گزارش — برای اعمال: --apply")

    cleanup_temp(args.apply)
    apply_patches(args.apply)
    manual_actions()

    print("\n" + "═" * 60)
    print("  ✅ پس از اعمال، دوباره اسکن کنید:")
    print('     python project_analyzer.py . --no-network \\')
    print('       --exclude ".pnpm-store/*" --exclude "node_modules/*" \\')
    print('       --exclude "reports/*" --exclude ".security_backup/*"')
    print("═" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())