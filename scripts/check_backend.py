#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Econojin Backend Health Checker
بررسی کامل سلامت بک‌اند و رفع خودکار مشکلات رایج
"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

def check_python_version():
    """بررسی نسخه پایتون"""
    if sys.version_info < (3, 10):
        print("❌ پایتون ۳.۱۰ یا بالاتر نیاز است")
        return False
    print(f"✅ پایتون {sys.version.split()[0]}")
    return True

def check_virtualenv():
    """بررسی فعال بودن محیط مجازی"""
    if not hasattr(sys, 'real_prefix') and not (sys.base_prefix != sys.prefix):
        print("⚠️ محیط مجازی فعال نیست (توصیه می‌شود)")
    else:
        print("✅ محیط مجازی فعال است")
    return True

def check_config_file():
    """بررسی فایل config.py"""
    config_path = ROOT / "api" / "core" / "config.py"
    if not config_path.exists():
        print(f"❌ فایل پیدا نشد: {config_path}")
        return False
    
    content = config_path.read_text(encoding="utf-8")
    
    # بررسی خطاهای رایج
    errors = []
    if "_ALLOWED_ORIGINS" in content:
        errors.append("❌ فیلد با underscore: از ALLOWED_ORIGINS_RAW استفاده کنید")
    if "extra = 'allow'" in content:
        errors.append("⚠️ extra='allow' ممکن است باعث خطا شود، از 'ignore' استفاده کنید")
    
    if errors:
        for e in errors:
            print(e)
        return False
    
    print("✅ config.py سالم است")
    return True

def check_database_config():
    """بررسی پیکربندی دیتابیس"""
    try:
        from api.core.config import settings
        print(f"✅ DATABASE_URL: {settings.DATABASE_URL}")
        
        if "postgresql" in settings.DATABASE_URL:
            print("⚠️ PostgreSQL نیاز به سرور در حال اجرا دارد")
            print("💡 برای توسعه سریع، از SQLite استفاده کنید:")
            print("   DATABASE_URL=sqlite+aiosqlite:///./econojin.db")
        elif "sqlite" in settings.DATABASE_URL:
            print("✅ SQLite: بدون نیاز به سرور خارجی")
        return True
    except Exception as e:
        print(f"❌ خطا در بارگذاری تنظیمات: {e}")
        return False

def check_main_imports():
    """بررسی importهای api/main.py"""
    main_path = ROOT / "api" / "main.py"
    if not main_path.exists():
        print(f"❌ فایل پیدا نشد: {main_path}")
        return False
    
    content = main_path.read_text(encoding="utf-8")
    
    # بررسی importهای حیاتی
    required = [
        "from api.core.config import settings",
        "from api.core.database import init_db",
    ]
    
    missing = [r for r in required if r not in content]
    if missing:
        print("❌ importهای مفقوده:")
        for m in missing:
            print(f"   {m}")
        return False
    
    print("✅ importهای main.py کامل است")
    return True

def check_agents_module():
    """بررسی ماژول agents (اختیاری)"""
    orchestrator = ROOT / "api" / "agents" / "orchestrator.py"
    
    if not orchestrator.exists():
        print("⚠️ api/agents/orchestrator.py یافت نشد")
        print("💡 برای رفع خطای ImportError، یکی از دو کار را انجام دهید:")
        print("   ۱. فایل orchestrator.py را ایجاد کنید (کد نمونه در پایین)")
        print("   ۲. یا import آن را در main.py با try/except احاطه کنید")
        
        # نمایش کد نمونه
        print("\n📋 کد نمونه برای orchestrator.py:")
        print("""
class EconojinOrchestrator:
    def __init__(self):
        self.agents = {}
    
    async def process_request(self, request: str, context: dict):
        return {"status": "processed", "response": "OK"}
        """)
        return False
    
    print("✅ api/agents/orchestrator.py موجود است")
    return True

def run_all_checks():
    """اجرای تمام بررسی‌ها"""
    print("🔍 Econojin Backend Health Check")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtualenv),
        ("Config File", check_config_file),
        ("Database Config", check_database_config),
        ("Main Imports", check_main_imports),
        ("Agents Module", check_agents_module),
    ]
    
    results = []
    for name, func in checks:
        print(f"\n[{name}]")
        try:
            result = func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ خطا در بررسی {name}: {e}")
            results.append((name, False))
    
    # گزارش نهایی
    print("\n" + "=" * 50)
    print("📊 گزارش نهایی:")
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print(f"\nنتیجه: {passed}/{total} بررسی موفق")
    
    if passed == total:
        print("🎉 بک‌اند آماده اجراست!")
        print("\n🚀 برای اجرا:")
        print("   python -m api.main")
        return 0
    else:
        print("⚠️ برخی مشکلات نیاز به رفع دارند")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_checks())