#!/usr/bin/env python3
"""
Econojin Frontend Analyzer
تحلیل‌گر ساختار فرانت‌اند برای شناسایی نقاط ورود، روتینگ و فایل‌های گم‌شده.
"""
import os
import re
from pathlib import Path

def analyze_frontend():
    root = Path("apps/web/src")
    if not root.exists():
        print("❌ پوشه apps/web/src یافت نشد. لطفاً مسیر را بررسی کنید.")
        return

    print("🔍 در حال آنالیز ساختار فرانت‌اند Econojin...\n")

    # ۱. بررسی فایل‌های ورودی اصلی
    print("📌 ۱. بررسی نقاط ورود (Entry Points):")
    entry_files = ["index.html", "main.tsx", "main.jsx", "App.tsx", "App.jsx"]
    for f in entry_files:
        path = root.parent / f if f == "index.html" else root / f
        if path.exists():
            print(f"   ✅ {f} یافت شد.")
        else:
            print(f"   ❌ {f} یافت نشد! (باید ایجاد شود)")

    # ۲. تحلیل App.tsx برای روتینگ
    print("\n📌 ۲. بررسی تنظیمات Routing در App.tsx:")
    app_tsx = root / "App.tsx"
    if app_tsx.exists():
        content = app_tsx.read_text(encoding="utf-8")
        if "BrowserRouter" in content or "HashRouter" in content:
            print("   ✅ کتابخانه Routing (React Router) شناسایی شد.")
        else:
            print("   ⚠️ هشدار: هیچ Routerای در App.tsx یافت نشد.")
        
        # استخراج مسیرهای تعریف شده
        routes = re.findall(r'<Route\s+path=["\']([^"\']+)["\']', content)
        print(f"   🛣️ مسیرهای (Routes) یافت شده: {', '.join(routes) if routes else 'هیچ'}")
    else:
        print("   ❌ فایل App.tsx وجود ندارد.")

    # ۳. بررسی صفحات (Pages) موجود
    print("\n📌 ۳. بررسی صفحات (Pages) موجود:")
    pages_dir = root / "pages"
    if pages_dir.exists():
        pages = [f.stem for f in pages_dir.iterdir() if f.is_file() and f.suffix in ['.tsx', '.jsx']]
        print(f"   ✅ صفحات یافت شده: {', '.join(pages)}")
        
        # بررسی صفحات حیاتی که باید وجود داشته باشند
        required_pages = ["HomePage", "Dashboard", "SimulatorsPage", "EcocoinPage"]
        missing = [p for p in required_pages if not any(p.lower() in page.lower() for page in pages)]
        if missing:
            print(f"   ⚠️ صفحات حیاتی گم‌شده: {', '.join(missing)}")
    else:
        print("   ❌ پوشه pages/ یافت نشد.")

    # ۴. بررسی کامپوننت‌های حیاتی
    print("\n📌 ۴. بررسی کامپوننت‌های حیاتی (Layout, Header, Sidebar):")
    components_dir = root / "components"
    vital_components = ["Layout", "Header", "Sidebar", "Footer"]
    if components_dir.exists():
        for vc in vital_components:
            # جستجو برای فایل‌هایی که با این نام شروع می‌شوند
            matches = [f.name for f in components_dir.rglob(f"{vc}*") if f.is_file()]
            if matches:
                print(f"   ✅ {vc}: {', '.join(matches)}")
            else:
                print(f"   ❌ {vc}: یافت نشد (باید ایجاد شود)")

    print("\n✅ آنالیز فرانت‌اند به پایان رسید.")
    print("💡 پیشنهاد: بر اساس خروجی بالا، فایل‌های گم‌شده را ایجاد یا اصلاح خواهیم کرد.")

if __name__ == "__main__":
    analyze_frontend()