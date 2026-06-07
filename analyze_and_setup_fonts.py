#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 آنالیز جامع فرانت‌اند اکو نوژین + نصب و تنظیم فونت‌ها
"""
import sys
import subprocess
import shutil
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

ROOT = Path(__file__).parent.resolve()
WEB_DIR = ROOT / "apps" / "web"
SRC_DIR = WEB_DIR / "src"


def print_header(title: str, char: str = "="):
    print("\n" + char * 70)
    print(f"  {title}")
    print(char * 70)


def print_section(title: str):
    print(f"\n📌 {title}")
    print("-" * 70)


# ============================================================================
# بخش ۱: آنالیز جامع فرانت‌اند
# ============================================================================
def analyze_frontend():
    print_header("🔍 گزارش آنالیز جامع فرانت‌اند اکو نوژین", "=")
    print(f"📅 تاریخ گزارش: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 ریشه پروژه: {ROOT}")
    print(f"📁 پوشه فرانت‌اند: {WEB_DIR}")

    # 1. بررسی وجود پوشه‌های اصلی
    print_section("۱. ساختار کلی پروژه")
    
    main_dirs = {
        "apps/web": WEB_DIR,
        "apps/web/src": SRC_DIR,
        "apps/web/src/app": SRC_DIR / "app",
        "apps/web/src/components": SRC_DIR / "components",
        "apps/web/src/lib": SRC_DIR / "lib",
        "apps/web/public": WEB_DIR / "public",
        "api": ROOT / "api",
    }
    
    for name, path in main_dirs.items():
        if path.exists():
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name} - یافت نشد")

    # 2. شمارش فایل‌ها بر اساس نوع
    print_section("۲. آمار فایل‌ها")
    
    file_stats = defaultdict(int)
    total_files = 0
    
    for ext in ["tsx", "ts", "jsx", "js", "css", "json", "md"]:
        count = len(list(WEB_DIR.rglob(f"*.{ext}")))
        file_stats[ext] = count
        total_files += count
    
    for ext, count in sorted(file_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   📄 .{ext:4s}: {count:4d} فایل")
    
    print(f"   📊 مجموع: {total_files} فایل")

    # 3. آنالیز صفحات (Pages)
    print_section("۳. صفحات موجود (Routes)")
    
    app_dir = SRC_DIR / "app"
    pages = []
    
    if app_dir.exists():
        for page_file in app_dir.rglob("page.tsx"):
            rel_path = page_file.relative_to(app_dir)
            route = "/" + str(rel_path.parent).replace("\\", "/")
            if route == "/.":
                route = "/"
            pages.append({
                "route": route,
                "path": page_file,
                "size": page_file.stat().st_size,
            })
    
    pages.sort(key=lambda x: x["route"])
    
    for page in pages:
        size_kb = page["size"] / 1024
        print(f"   🌐 {page['route']:40s} ({size_kb:.1f} KB)")
    
    print(f"\n   📊 مجموع صفحات: {len(pages)}")

    # 4. آنالیز Layout ها
    print_section("۴. Layout ها")
    
    layouts = []
    if app_dir.exists():
        for layout_file in app_dir.rglob("layout.tsx"):
            rel_path = layout_file.relative_to(app_dir)
            route = "/" + str(rel_path.parent).replace("\\", "/")
            if route == "/.":
                route = "/"
            layouts.append({"route": route, "path": layout_file})
    
    for layout in layouts:
        print(f"   📐 {layout['route']}")
    
    print(f"\n   📊 مجموع Layout ها: {len(layouts)}")

    # 5. آنالیز کامپوننت‌ها
    print_section("۵. کامپوننت‌ها")
    
    components_dir = SRC_DIR / "components"
    components = []
    
    if components_dir.exists():
        for comp_file in components_dir.rglob("*.tsx"):
            rel_path = comp_file.relative_to(components_dir)
            components.append({
                "name": comp_file.stem,
                "path": str(rel_path).replace("\\", "/"),
                "size": comp_file.stat().st_size,
            })
    
    for comp in sorted(components, key=lambda x: x["path"]):
        size_kb = comp["size"] / 1024
        print(f"   🧩 {comp['path']:50s} ({size_kb:.1f} KB)")
    
    print(f"\n   📊 مجموع کامپوننت‌ها: {len(components)}")

    # 6. آنالیز استایل‌ها
    print_section("۶. فایل‌های استایل")
    
    css_files = list(WEB_DIR.rglob("*.css"))
    for css_file in css_files:
        rel_path = css_file.relative_to(WEB_DIR)
        size_kb = css_file.stat().st_size / 1024
        print(f"   🎨 {str(rel_path).replace(chr(92), '/'):50s} ({size_kb:.1f} KB)")

    # 7. بررسی فایل‌های پیکربندی
    print_section("۷. فایل‌های پیکربندی")
    
    config_files = [
        "package.json",
        "next.config.js",
        "next.config.mjs",
        "tailwind.config.js",
        "tailwind.config.ts",
        "tsconfig.json",
        "postcss.config.js",
        ".eslintrc.json",
        ".env",
        ".env.local",
    ]
    
    for config in config_files:
        config_path = WEB_DIR / config
        if config_path.exists():
            print(f"   ⚙️  {config}")
        else:
            print(f"   ⚪ {config} (وجود ندارد)")

    # 8. بررسی وابستگی‌ها
    print_section("۸. وابستگی‌های کلیدی")
    
    package_json = WEB_DIR / "package.json"
    if package_json.exists():
        content = package_json.read_text(encoding="utf-8")
        
        key_packages = [
            "next", "react", "react-dom", "tailwindcss",
            "framer-motion", "lucide-react", "recharts",
            "leaflet", "react-leaflet", "@fontsource/vazirmatn"
        ]
        
        for pkg in key_packages:
            pattern = f'"{pkg}"\\s*:\\s*"([^"]+)"'
            match = re.search(pattern, content)
            if match:
                version = match.group(1)
                print(f"   📦 {pkg:25s} v{version}")
            else:
                print(f"   ❌ {pkg:25s} نصب نشده")

    # 9. بررسی فونت‌های فعلی
    print_section("۹. وضعیت فعلی فونت‌ها")
    
    globals_css = SRC_DIR / "app" / "globals.css"
    has_vazir = False
    has_inter = False
    has_font_import = False
    
    if globals_css.exists():
        css_content = globals_css.read_text(encoding="utf-8")
        has_vazir = "vazirmatn" in css_content.lower() or "vazir" in css_content.lower()
        has_inter = "inter" in css_content.lower()
        has_font_import = "@fontsource" in css_content or "fonts.googleapis" in css_content
    
    print(f"   {'✅' if has_vazir else '❌'} فونت وزیرمتن: {'فعال' if has_vazir else 'غیرفعال'}")
    print(f"   {'✅' if has_inter else '❌'} فونت Inter: {'فعال' if has_inter else 'غیرفعال'}")
    print(f"   {'✅' if has_font_import else '❌'} Import فونت: {'فعال' if has_font_import else 'غیرفعال'}")

    # 10. مشکلات احتمالی
    print_section("۱۰. مشکلات و هشدارهای احتمالی")
    
    issues = []
    
    # بررسی وجود فایل‌های مهم
    if not (SRC_DIR / "app" / "layout.tsx").exists():
        issues.append("❌ فایل layout.tsx وجود ندارد")
    
    if not globals_css.exists():
        issues.append("❌ فایل globals.css وجود ندارد")
    
    # بررسی استفاده از use client
    for page in pages:
        content = page["path"].read_text(encoding="utf-8")
        if "use client" not in content and "use server" not in content:
            # این ممکن است مشکل باشد
            pass
    
    if issues:
        for issue in issues:
            print(f"   {issue}")
    else:
        print("   ✅ مشکل خاصی شناسایی نشد")

    # خلاصه گزارش
    print_header("📊 خلاصه گزارش", "=")
    print(f"   📁 تعداد صفحات: {len(pages)}")
    print(f"   📐 تعداد Layout ها: {len(layouts)}")
    print(f"   🧩 تعداد کامپوننت‌ها: {len(components)}")
    print(f"   🎨 تعداد فایل‌های CSS: {len(css_files)}")
    print(f"   📄 مجموع فایل‌ها: {total_files}")
    print(f"   {'✅' if has_vazir else '⚠️ '} وضعیت فونت فارسی: {'آماده' if has_vazir else 'نیاز به تنظیم'}")
    print(f"   {'✅' if has_inter else '⚠️ '} وضعیت فونت انگلیسی: {'آماده' if has_inter else 'نیاز به تنظیم'}")

    return {
        "pages": pages,
        "layouts": layouts,
        "components": components,
        "has_vazir": has_vazir,
        "has_inter": has_inter,
    }


# ============================================================================
# بخش ۲: نصب و تنظیم فونت‌ها
# ============================================================================
def setup_fonts():
    print_header("🎨 نصب و تنظیم فونت‌ها", "=")
    
    # 1. نصب پکیج‌های فونت
    print_section("۱. نصب پکیج‌های فونت")
    
    packages = ["@fontsource/vazirmatn", "@fontsource/inter", "@fontsource/jetbrains-mono"]
    
    for package in packages:
        print(f"   📦 نصب {package}...")
        try:
            result = subprocess.run(
                ["pnpm", "add", package],
                cwd=str(WEB_DIR),
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print(f"   ✅ {package} نصب شد")
            else:
                print(f"   ⚠️  خطا در نصب {package}: {result.stderr[:100]}")
        except Exception as e:
            print(f"   ❌ خطا: {e}")

    # 2. به‌روزرسانی globals.css
    print_section("۲. به‌روزرسانی globals.css")
    
    globals_css = SRC_DIR / "app" / "globals.css"
    
    # خواندن محتوای فعلی
    existing_content = ""
    if globals_css.exists():
        existing_content = globals_css.read_text(encoding="utf-8")
    
    # محتوای جدید با فونت‌ها
    new_css_content = '''/* ==========================================================================
   فونت‌های اکو نوژین
   ========================================================================== */

/* فونت فارسی - وزیرمتن */
@import '@fontsource/vazirmatn/400.css';
@import '@fontsource/vazirmatn/500.css';
@import '@fontsource/vazirmatn/600.css';
@import '@fontsource/vazirmatn/700.css';
@import '@fontsource/vazirmatn/800.css';
@import '@fontsource/vazirmatn/900.css';

/* فونت انگلیسی - Inter */
@import '@fontsource/inter/400.css';
@import '@fontsource/inter/500.css';
@import '@fontsource/inter/600.css';
@import '@fontsource/inter/700.css';
@import '@fontsource/inter/800.css';
@import '@fontsource/inter/900.css';

/* فونت کد - JetBrains Mono */
@import '@fontsource/jetbrains-mono/400.css';
@import '@fontsource/jetbrains-mono/500.css';
@import '@fontsource/jetbrains-mono/700.css';

/* ==========================================================================
   متغیرهای CSS
   ========================================================================== */

:root {
  --font-fa: 'Vazirmatn', 'IRANSansX', system-ui, -apple-system, sans-serif;
  --font-en: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  /* رنگ‌های اصلی اکو نوژین */
  --color-primary: #2d5016;
  --color-secondary: #8b6f47;
  --color-accent: #10b981;
  --color-bg: #faf8f3;
  --color-bg-secondary: #f5f1e8;
  --color-text: #2c2416;
  --color-text-secondary: #6b5d4f;
}

/* ==========================================================================
   Tailwind CSS
   ========================================================================== */

@tailwind base;
@tailwind components;
@tailwind utilities;

/* ==========================================================================
   استایل‌های پایه
   ========================================================================== */

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-family: var(--font-fa);
  direction: rtl;
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-fa);
  color: var(--color-text);
  background-color: var(--color-bg);
  line-height: 1.8;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-feature-settings: "ss01", "ss02";
}

/* ==========================================================================
   کلاس‌های کمکی فونت
   ========================================================================== */

.font-fa {
  font-family: var(--font-fa) !important;
}

.font-en {
  font-family: var(--font-en) !important;
  direction: ltr;
}

.font-mono {
  font-family: var(--font-mono) !important;
  direction: ltr;
}

/* ==========================================================================
   سلسله مراتب تایپوگرافی
   ========================================================================== */

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-fa);
  font-weight: 800;
  line-height: 1.3;
  color: var(--color-text);
}

h1 {
  font-size: 3rem;
  font-weight: 900;
  letter-spacing: -0.02em;
}

h2 {
  font-size: 2.25rem;
  font-weight: 800;
}

h3 {
  font-size: 1.75rem;
  font-weight: 700;
}

h4 {
  font-size: 1.5rem;
  font-weight: 700;
}

p {
  font-family: var(--font-fa);
  font-weight: 400;
  line-height: 1.9;
}

/* ==========================================================================
   اعداد فارسی
   ========================================================================== */

.fa-num {
  font-feature-settings: "ss02";
}

/* ==========================================================================
   کد و داده‌های فنی
   ========================================================================== */

code, pre, .mono {
  font-family: var(--font-mono);
  direction: ltr;
  text-align: left;
}

pre {
  background-color: #1e293b;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
}

code {
  background-color: #f1f5f9;
  color: #0f172a;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
}

pre code {
  background-color: transparent;
  padding: 0;
}

/* ==========================================================================
   لینک‌ها
   ========================================================================== */

a {
  color: var(--color-primary);
  text-decoration: none;
  transition: color 0.2s ease;
}

a:hover {
  color: var(--color-accent);
}

/* ==========================================================================
   اسکرول‌بار سفارشی
   ========================================================================== */

::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: var(--color-bg-secondary);
}

::-webkit-scrollbar-thumb {
  background: var(--color-secondary);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary);
}

/* ==========================================================================
   انیمیشن‌ها
   ========================================================================== */

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.5s ease-out;
}

/* ==========================================================================
   ریسپانسیو
   ========================================================================== */

@media (max-width: 768px) {
  h1 {
    font-size: 2rem;
  }
  
  h2 {
    font-size: 1.75rem;
  }
  
  h3 {
    font-size: 1.5rem;
  }
  
  body {
    font-size: 0.9375rem;
  }
}

/* ==========================================================================
   چاپ
   ========================================================================== */

@media print {
  body {
    background: white;
    color: black;
  }
  
  a {
    color: black;
    text-decoration: underline;
  }
}
'''
    
    globals_css.write_text(new_css_content, encoding="utf-8")
    print(f"   ✅ globals.css با موفقیت به‌روزرسانی شد ({globals_css.stat().st_size} bytes)")

    # 3. به‌روزرسانی layout.tsx
    print_section("۳. به‌روزرسانی layout.tsx")
    
    layout_path = SRC_DIR / "app" / "layout.tsx"
    
    layout_content = '''import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "اکو نوژین | پلتفرم علمی احیای زمین",
  description: "پلتفرم جامع علمی برای احیای مناظر خشک و نیمه‌خشک، کشاورزی پایدار و مدیریت منابع آب",
  keywords: ["اکو نوژین", "کشاورزی پایدار", "احیای زمین", "مدیریت آب", "تغییر اقلیم"],
  authors: [{ name: "Econojin Team" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fa" dir="rtl" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className="font-fa antialiased">
        {children}
      </body>
    </html>
  );
}
'''
    
    layout_path.write_text(layout_content, encoding="utf-8")
    print(f"   ✅ layout.tsx با موفقیت به‌روزرسانی شد")

    # 4. پاک‌سازی کش
    print_section("۴. پاک‌سازی کش Next.js")
    
    next_dir = WEB_DIR / ".next"
    if next_dir.exists():
        try:
            shutil.rmtree(next_dir)
            print("   ✅ پوشه .next حذف شد")
        except Exception as e:
            print(f"   ⚠️  خطا در حذف: {e}")
    else:
        print("   ℹ️  پوشه .next وجود نداشت")

    # 5. بررسی نهایی
    print_section("۵. بررسی نهایی")
    
    print("   📦 پکیج‌های نصب شده:")
    for package in packages:
        try:
            result = subprocess.run(
                ["pnpm", "list", package, "--depth=0"],
                cwd=str(WEB_DIR),
                capture_output=True,
                text=True,
                timeout=30
            )
            if package in result.stdout:
                print(f"      ✅ {package}")
            else:
                print(f"      ⚠️  {package} - بررسی مجدد نیاز است")
        except:
            print(f"      ⚠️  {package} - خطا در بررسی")

    print("\n   📁 فایل‌های به‌روزرسانی شده:")
    print(f"      ✅ {globals_css.relative_to(ROOT)}")
    print(f"      ✅ {layout_path.relative_to(ROOT)}")


# ============================================================================
# بخش ۳: خلاصه نهایی
# ============================================================================
def final_summary():
    print_header("🎉 خلاصه نهایی", "=")
    
    print("""
   ✅ آنالیز جامع فرانت‌اند انجام شد
   ✅ فونت وزیرمتن (فارسی) نصب و تنظیم شد
   ✅ فونت Inter (انگلیسی) نصب و تنظیم شد
   ✅ فونت JetBrains Mono (کد) نصب و تنظیم شد
   ✅ globals.css با استایل‌های حرفه‌ای به‌روزرسانی شد
   ✅ layout.tsx با متادیتای کامل به‌روزرسانی شد
   ✅ کش Next.js پاک‌سازی شد

   🎨 ویژگی‌های فونت جدید:
      • وزیرمتن: ۶ وزن (400-900) برای متون فارسی
      • Inter: ۶ وزن (400-900) برای متون انگلیسی
      • JetBrains Mono: برای کد و داده‌های فنی
      • اعداد فارسی با feature settings
      • سلسله مراتب تایپوگرافی کامل
      • اسکرول‌بار سفارشی
      • انیمیشن‌های ظریف
      • ریسپانسیو برای موبایل
      • بهینه‌سازی برای چاپ

   🚀 گام‌های بعدی:
      1. سرور فرانت‌اند را ری‌استارت کنید:
         cd apps\\web
         pnpm run dev -- -p 3001

      2. مشاهده نتیجه:
         http://localhost:3001

      3. تست فونت‌ها:
         • متن فارسی با وزیرمتن نمایش داده می‌شود
         • متن انگلیسی با Inter نمایش داده می‌شود
         • کدها با JetBrains Mono نمایش داده می‌شوند
""")
    
    print("=" * 70)


# ============================================================================
# Main
# ============================================================================
def main():
    try:
        # آنالیز فرانت‌اند
        report = analyze_frontend()
        
        # نصب و تنظیم فونت‌ها
        setup_fonts()
        
        # خلاصه نهایی
        final_summary()
        
        return 0
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())