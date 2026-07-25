#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Econojin Synchronization Audit Script
این اسکریپت شکاف بین بک‌اند، روتینگ فرانت‌اند و منوی هدر را شناسایی می‌کند.
"""
import re
from pathlib import Path

PROJECT_ROOT = Path("D:/econojin.com")

def extract_backend_routes():
    """استخراج مسیرها از apps/main.py"""
    main_py = PROJECT_ROOT / "apps" / "main.py"
    if not main_py.exists():
        return []
    
    content = main_py.read_text(encoding="utf-8")
    # پیدا کردن الگوهایی مثل: app.include_router(..., prefix="/api/v1/users", ...)
    routes = re.findall(r'prefix\s*=\s*["\']([^"\']+)["\']', content)
    # تمیزکاری و یکتاسازی
    return list(set([r.strip("/") for r in routes if r]))

def extract_frontend_routes():
    """استخراج مسیرها از apps/web/src/App.tsx"""
    app_tsx = PROJECT_ROOT / "apps" / "web" / "src" / "App.tsx"
    if not app_tsx.exists():
        return []
    
    content = app_tsx.read_text(encoding="utf-8")
    # پیدا کردن الگوهایی مثل: <Route path="dashboard" element={...} />
    routes = re.findall(r'<Route\s+path=["\']([^"\']+)["\']', content)
    return list(set([r.strip("/") for r in routes if r and r != "*"]))

def extract_header_links():
    """استخراج لینک‌ها از apps/web/src/components/Header.tsx"""
    header_tsx = PROJECT_ROOT / "apps" / "web" / "src" / "components" / "Header.tsx"
    if not header_tsx.exists():
        return []
    
    content = header_tsx.read_text(encoding="utf-8")
    # پیدا کردن الگوهایی مثل: href: "/dashboard" یا to="/dashboard"
    links = re.findall(r'(?:href|to)\s*[:=]\s*["\']([^"\']+)["\']', content)
    return list(set([l.strip("/") for l in links if l]))

def main():
    print("🔍 در حال اسکن پروژه برای شناسایی شکاف‌های همگام‌سازی...\n")
    
    backend_routes = extract_backend_routes()
    frontend_routes = extract_frontend_routes()
    header_links = extract_header_links()
    
    print(f"📊 آمار کلی:")
    print(f"   • مسیرهای بک‌اند (API Prefixes): {len(backend_routes)}")
    print(f"   • مسیرهای فرانت‌اند (App.tsx): {len(frontend_routes)}")
    print(f"   • لینک‌های منوی هدر (Header.tsx): {len(header_links)}\n")

    print("="*60)
    print("🚨 گزارش ناهماهنگی (Drift Report)")
    print("="*60)

    # ۱. لینک‌های هدر که صفحه‌ای در App.tsx ندارند (Broken Links)
    broken_links = [link for link in header_links if link not in frontend_routes and not link.startswith("api")]
    if broken_links:
        print("\n❌ ۱. لینک‌های شکسته در هدر (در App.tsx وجود ندارند):")
        for link in broken_links:
            print(f"   • /{link}")

    # ۲. صفحاتی که در App.tsx هستند اما در منوی هدر نیستند (Hidden Pages)
    hidden_pages = [route for route in frontend_routes if route not in header_links and not route.startswith("api") and ":" not in route]
    if hidden_pages:
        print("\n⚠️  ۲. صفحات پنهان (در App.tsx هستند اما در منوی هدر نیستند):")
        for page in hidden_pages:
            print(f"   • /{page}")

    # ۳. فایل‌های صفحه‌ای که اصلاً در App.tsx ایمپورت نشده‌اند (Dead Code)
    pages_dir = PROJECT_ROOT / "apps" / "web" / "src" / "pages"
    if pages_dir.exists():
        app_content = (PROJECT_ROOT / "apps" / "web" / "src" / "App.tsx").read_text(encoding="utf-8")
        dead_pages = []
        for page_file in pages_dir.glob("*.tsx"):
            page_name = page_file.stem
            # بررسی اینکه آیا این صفحه در App.tsx ایمپورت شده است یا خیر
            if f'import {page_name}' not in app_content and f'import {page_name}' not in app_content.replace("Page", ""):
                dead_pages.append(page_file.name)
        
        if dead_pages:
            print("\n🗑️ ۳. فایل‌های مرده (Dead Code) در پوشه pages/ (ایمپورت نشده‌اند):")
            for page in dead_pages[:10]: # نمایش حداکثر ۱۰ مورد
                print(f"   • {page}")
            if len(dead_pages) > 10:
                print(f"   • ... و {len(dead_pages) - 10} مورد دیگر")

    print("\n" + "="*60)
    print("✅ اسکن به پایان رسید. بر اساس این گزارش، فایل‌ها را اصلاح خواهیم کرد.")

if __name__ == "__main__":
    main()