#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📦 Econojin Dependency Installer
نصب خودکار پکیج‌های npm مفقوده برای رفع خطاهای Build
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "apps" / "web"
if not WEB.exists():
    WEB = ROOT / "web"


def run_command(cmd: list, cwd: Path):
    """اجرای دستور با نمایش خروجی"""
    print(f"🔄 executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0


def install_missing_deps():
    """نصب پکیج‌های مفقوده"""

    # پکیج‌های اصلی UI که در کامپوننت‌ها استفاده شده‌اند
    missing_deps = [
        "class-variance-authority@^0.7.0",
        "clsx@^2.1.0",
        "tailwind-merge@^2.3.0",
        "@tanstack/react-query@^5.50.0",  # برای هوک‌ها
    ]

    print("📦 نصب پکیج‌های مفقوده...")

    # استفاده از pnpm با میرور سریع
    cmd = [
        "pnpm",
        "add",
        "--registry=https://registry.npmmirror.com",
        "--prefer-offline",
    ] + missing_deps

    if run_command(cmd, WEB):
        print("✅ پکیج‌ها با موفقیت نصب شدند")
        return True
    else:
        print("❌ خطا در نصب پکیج‌ها")
        return False


def create_supabase_middleware():
    """ایجاد فایل middleware مفقوده"""

    middleware_content = """// Placeholder - Supabase middleware not configured
// برای فعال‌سازی: ۱. نصب @supabase/ssr  ۲. تنظیم متغیرهای محیطی

import { type NextRequest } from 'next/server'

export async function updateSession(request: NextRequest) {
  // Placeholder: در نسخه واقعی، سشن Supabase را آپدیت می‌کند
  return request
}

export async function getSession(request: NextRequest) {
  // Placeholder: در نسخه واقعی، سشن کاربر را برمی‌گرداند
  return null
}
"""

    middleware_path = WEB / "src" / "lib" / "supabase" / "middleware.ts"
    middleware_path.parent.mkdir(parents=True, exist_ok=True)
    middleware_path.write_text(middleware_content, encoding="utf-8")
    print(f"✅ ایجاد شد: {{middleware_path.relative_to(ROOT)}}")

    # اصلاح middleware.ts ریشه اگر وجود دارد
    root_middleware = WEB / "middleware.ts"
    if root_middleware.exists():
        content = root_middleware.read_text(encoding="utf-8")
        if "updateSession" in content and "from '@/lib/supabase/middleware'" in content:
            # فایل از قبل درست است
            pass
        else:
            # بازنویسی با import صحیح
            new_content = """import { type NextRequest } from 'next/server'
import { updateSession } from '@/lib/supabase/middleware'

export async function middleware(request: NextRequest) {
  return await updateSession(request)
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\\\.png$).*)'],
}
"""
            root_middleware.write_text(new_content, encoding="utf-8")
            print("✅ middleware.ts ریشه اصلاح شد")


def main():
    print("📦 Econojin Dependency Installer")
    print("=" * 50)

    try:
        # ۱. نصب پکیج‌های npm
        if not install_missing_deps():
            return 1

        # ۲. ایجاد فایل‌های مفقوده Supabase
        create_supabase_middleware()

        print("\n" + "=" * 50)
        print("✅ نصب وابستگی‌ها تکمیل شد!")
        print("=" * 50)
        print("\n🚀 حالا می‌توانید بیلد را اجرا کنید:")
        print(f"   cd {{WEB}}")
        print("   pnpm run build")
        print("=" * 50)
        return 0

    except Exception as e:
        print(f"\n❌ خطا: {{e}}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
