#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 آنالیزور وضعیت فعلی پروژه اکو نوژین
بررسی فایل‌های فرانت‌اند و بک‌اند قبل از بازنویسی
"""
import sys
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.resolve()
WEB_SRC = ROOT / "apps" / "web" / "src"
API_DIR = ROOT / "api"
REPORT_FILE = ROOT / "current_state_report.json"

# دسته‌بندی‌های گزارش
KEEP = "✅ نگه‌داری (سالم و ضروری)"
REVIEW = "⚠️ بررسی/به‌روزرسانی (نیاز به تطبیق)"
DELETE = "🗑️ حذف (تکراری، پشتیبان یا منسوخ)"
MISSING = "❌ مفقود (باید ایجاد شود)"

def get_files(directory: Path, extensions: list) -> list:
    """دریافت لیست فایل‌ها با پسوند خاص"""
    if not directory.exists():
        return []
    files = []
    for ext in extensions:
        files.extend(directory.rglob(f"*{ext}"))
    # فیلتر کردن node_modules و .next
    return [f for f in files if "node_modules" not in f.parts and ".next" not in f.parts and "__pycache__" not in f.parts]

def analyze_frontend():
    print("\n" + "="*70)
    print("🎨 آنالیز فرانت‌اند (apps/web/src)")
    print("="*70)
    
    report = {"keep": [], "review": [], "delete": [], "missing": []}
    
    if not WEB_SRC.exists():
        print(f"❌ دایرکتوری {WEB_SRC} یافت نشد!")
        return report

    # 1. بررسی فایل‌های پشتیبان مزاحم (.legacy-backup)
    backup_files = list(WEB_SRC.rglob("*.legacy-backup"))
    if backup_files:
        print(f"\n🗑️ یافت شد: {len(backup_files)} فایل پشتیبان مزاحم (باید حذف شوند)")
        for f in backup_files[:10]: # نمایش 10 تای اول
            print(f"   - {f.relative_to(WEB_SRC)}")
            report["delete"].append(str(f.relative_to(WEB_SRC)))
        if len(backup_files) > 10:
            print(f"   ... و {len(backup_files) - 10} فایل دیگر")

    # 2. بررسی کامپوننت‌های UI
    ui_dir = WEB_SRC / "components" / "ui"
    if ui_dir.exists():
        ui_files = [f.name for f in ui_dir.glob("*.tsx")]
        print(f"\n✅ کامپوننت‌های UI یافت شده ({len(ui_files)} مورد):")
        core_components = ["button.tsx", "card.tsx", "input.tsx", "label.tsx", "badge.tsx", "alert.tsx"]
        for comp in core_components:
            if comp in ui_files:
                print(f"   ✅ {comp} ({KEEP})")
                report["keep"].append(f"components/ui/{comp}")
            else:
                print(f"   ❌ {comp} ({MISSING})")
                report["missing"].append(f"components/ui/{comp}")
        
        # کامپوننت‌های اضافی که ممکن است نیاز به بررسی داشته باشند
        extra_ui = [f for f in ui_files if f not in core_components and not f.startswith(".")]
        if extra_ui:
            print(f"   ⚠️ سایر کامپوننت‌ها ({REVIEW}): {', '.join(extra_ui[:5])}")

    # 3. بررسی صفحات (Pages)
    app_dir = WEB_SRC / "app"
    if app_dir.exists():
        pages = [f.relative_to(app_dir) for f in app_dir.rglob("page.tsx")]
        print(f"\n📄 صفحات فعلی ({len(pages)} مورد):")
        important_pages = ["page.tsx", "layout.tsx", "login/page.tsx", "register/page.tsx", "profile/page.tsx", "admin/page.tsx"]
        for p in important_pages:
            path_obj = app_dir / p
            if path_obj.exists():
                print(f"   ✅ {p} ({REVIEW} - توسط اسکریپت جدید بازنویسی می‌شود)")
                report["review"].append(f"app/{p}")
            else:
                print(f"   ❌ {p} ({MISSING})")
                report["missing"].append(f"app/{p}")

    # 4. بررسی فایل‌های Lib
    lib_dir = WEB_SRC / "lib"
    if lib_dir.exists():
        lib_files = [f.name for f in lib_dir.glob("*.ts")]
        print(f"\n📚 فایل‌های کتابخانه (Lib):")
        if "api.ts" in lib_files:
            print(f"   ✅ api.ts ({REVIEW} - باید با سرویس‌های جدید ادغام شود)")
            report["review"].append("lib/api.ts")
        else:
            print(f"   ❌ api.ts ({MISSING})")
            report["missing"].append("lib/api.ts")
            
        if "utils.ts" in lib_files:
            print(f"   ✅ utils.ts ({KEEP})")
            report["keep"].append("lib/utils.ts")

    return report

def analyze_backend():
    print("\n" + "="*70)
    print("🛰️ آنالیز بک‌اند (api/)")
    print("="*70)
    
    report = {"keep": [], "review": [], "delete": [], "missing": []}
    
    if not API_DIR.exists():
        print(f"❌ دایرکتوری {API_DIR} یافت نشد!")
        return report

    # 1. فایل اصلی
    main_py = API_DIR / "main.py"
    if main_py.exists():
        print(f"\n✅ api/main.py یافت شد ({KEEP})")
        report["keep"].append("api/main.py")
    else:
        print(f"\n❌ api/main.py یافت نشد ({MISSING})")
        report["missing"].append("api/main.py")

    # 2. ماژول‌ها
    modules_dir = API_DIR / "modules"
    if modules_dir.exists():
        modules = [d.name for d in modules_dir.iterdir() if d.is_dir()]
        print(f"\n📦 ماژول‌های بک‌اند یافت شده ({len(modules)} مورد):")
        expected_modules = ["weather", "gis", "carbon", "hydrology", "auth", "shop"]
        for mod in expected_modules:
            if mod in modules:
                print(f"   ✅ {mod}/ ({KEEP})")
                report["keep"].append(f"api/modules/{mod}")
            else:
                print(f"   ⚠️ {mod}/ ({MISSING} - در صورت نیاز ایجاد می‌شود)")
                report["missing"].append(f"api/modules/{mod}")

    # 3. سرویس‌ها
    services_dir = API_DIR / "services"
    if services_dir.exists():
        services = [f.name for f in services_dir.glob("*.py")]
        print(f"\n⚙️ سرویس‌های بک‌اند ({len(services)} مورد):")
        for s in services[:5]:
            print(f"   ✅ {s} ({KEEP})")
            report["keep"].append(f"api/services/{s}")

    return report

def analyze_configs():
    print("\n" + "="*70)
    print("⚙️ آنالیز فایل‌های پیکربندی")
    print("="*70)
    
    configs_to_check = [
        ("apps/web/package.json", "پکیج‌های فرانت‌اند"),
        ("apps/web/tailwind.config.js", "پیکربندی Tailwind"),
        ("apps/web/tsconfig.json", "پیکربندی TypeScript"),
        ("api/core/config.py", "پیکربندی بک‌اند"),
        (".env.example", "متغیرهای محیطی نمونه"),
    ]
    
    print()
    for path_str, desc in configs_to_check:
        p = ROOT / path_str
        if p.exists():
            print(f"✅ {path_str:<35} ({KEEP} - {desc})")
        else:
            print(f"❌ {path_str:<35} ({MISSING} - {desc})")

def main():
    print("🔍 آنالیز وضعیت فعلی پروژه اکو نوژین")
    print(f"📁 ریشه پروژه: {ROOT}")
    
    fe_report = analyze_frontend()
    be_report = analyze_backend()
    analyze_configs()
    
    # ذخیره گزارش JSON
    full_report = {
        "frontend": fe_report,
        "backend": be_report
    }
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("📊 خلاصه اقدامات پیشنهادی:")
    print("="*70)
    
    total_delete = len(fe_report["delete"])
    if total_delete > 0:
        print(f"🗑️ 1. حذف {total_delete} فایل پشتیبان/تکراری مزاحم (بسیار مهم برای جلوگیری از خطای Build)")
    
    total_missing = len(fe_report["missing"]) + len(be_report["missing"])
    if total_missing > 0:
        print(f"➕ 2. ایجاد {total_missing} فایل مفقود یا سرویس جدید")
        
    print("🔄 3. بازنویسی صفحات و کامپوننت‌های اصلی با طراحی جدید اکو نوژین")
    print(f"💾 گزارش کامل در فایل ذخیره شد: {REPORT_FILE}")
    print("="*70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())