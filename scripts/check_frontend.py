#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Econojin Frontend Health Checker
بررسی کامل سلامت فرانت‌اند Next.js و رفع خودکار مشکلات
"""
import sys
import os
import json
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "web"

def check_node_version():
    """بررسی نسخه Node.js"""
    import subprocess
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        major = int(version.lstrip("v").split(".")[0])
        if major < 18:
            print(f"❌ Node.js 18+ نیاز است (نسخه فعلی: {version})")
            return False
        print(f"✅ Node.js {version}")
        return True
    except FileNotFoundError:
        print("❌ Node.js نصب نیست")
        return False
    except Exception as e:
        print(f"❌ خطا در بررسی Node.js: {e}")
        return False

def check_npm_packages():
    """بررسی package.json"""
    pkg_path = WEB / "package.json"
    if not pkg_path.exists():
        print(f"❌ فایل پیدا نشد: {pkg_path}")
        return False
    
    try:
        with open(pkg_path, encoding="utf-8") as f:
            pkg = json.load(f)
        
        required = ["next", "react", "react-dom"]
        missing = [p for p in required if p not in pkg.get("dependencies", {})]
        
        if missing:
            print(f"❌ پکیج‌های مفقوده: {missing}")
            return False
        
        print(f"✅ package.json سالم است ({len(pkg.get('dependencies', {}))} وابستگی)")
        return True
    except Exception as e:
        print(f"❌ خطا در خواندن package.json: {e}")
        return False

def check_app_router_structure():
    """بررسی ساختار App Router"""
    app_dir = WEB / "src" / "app"
    
    required_files = [
        app_dir / "layout.tsx",
        app_dir / "page.tsx",
    ]
    
    missing = [f for f in required_files if not f.exists()]
    if missing:
        print("❌ فایل‌های الزامی App Router مفقوده:")
        for f in missing:
            print(f"   {f.relative_to(ROOT)}")
        return False
    
    print("✅ ساختار App Router کامل است")
    return True

def check_page_exports():
    """بررسی export default در page.tsx و layout.tsx"""
    files = [
        ("page.tsx", WEB / "src" / "app" / "page.tsx"),
        ("layout.tsx", WEB / "src" / "app" / "layout.tsx"),
    ]
    
    errors = []
    for name, path in files:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        if "export default" not in content:
            errors.append(f"❌ {name}: export default پیدا نشد")
        else:
            print(f"✅ {name}: export default موجود است")
    
    if errors:
        for e in errors:
            print(e)
        return False
    return True

def check_layout_tsx():
    """بررسی محتوای layout.tsx برای خطاهای رایج"""
    layout_path = WEB / "src" / "app" / "layout.tsx"
    if not layout_path.exists():
        return True  # قبلاً بررسی شده
    
    content = layout_path.read_text(encoding="utf-8")
    errors = []
    
    # بررسی viewport برای themeColor
    if 'themeColor' in content and 'export const viewport' not in content:
        errors.append("⚠️ themeColor باید در export viewport باشد، نه metadata")
    
    # بررسی import استایل‌ها
    if "globals.css" not in content:
        errors.append("⚠️ import '@/styles/globals.css' ممکن است مفقوده باشد")
    
    if errors:
        for e in errors:
            print(e)
        return False
    
    print("✅ layout.tsx بدون خطای رایج است")
    return True

def check_node_modules():
    """بررسی وجود node_modules"""
    nm = WEB / "node_modules"
    if not nm.exists():
        print("❌ node_modules یافت نشد")
        print("💡 برای نصب:")
        print(f"   cd {WEB}")
        print("   npm install --registry=https://registry.npmmirror.com")
        return False
    
    # بررسی next
    next_bin = nm / ".bin" / "next.cmd" if os.name == "nt" else nm / ".bin" / "next"
    if not next_bin.exists():
        print("⚠️ باینری next پیدا نشد (ممکن است نصب ناقص باشد)")
        return False
    
    print("✅ node_modules کامل است")
    return True

def check_next_config():
    """بررسی next.config.js"""
    config_path = WEB / "next.config.js"
    if not config_path.exists():
        print("⚠️ next.config.js یافت نشد (مقادیر پیش‌فرض استفاده می‌شود)")
        return True
    
    content = config_path.read_text(encoding="utf-8")
    
    # بررسی تداخل i18n + output: export
    if "output: 'export'" in content and "i18n:" in content:
        print("❌ تداخل: i18n با output: 'export' سازگار نیست")
        print("💡 برای dev: output: 'export' را حذف یا کامنت کنید")
        return False
    
    print("✅ next.config.js بدون تداخل است")
    return True

def suggest_fixes():
    """پیشنهاد رفع مشکلات"""
    print("\n🔧 پیشنهادات رفع مشکل:")
    
    # اگر page.tsx مشکل دارد
    page = WEB / "src" / "app" / "page.tsx"
    if page.exists():
        content = page.read_text(encoding="utf-8")
        if "export default function Home" not in content:
            print("\n📋 محتوای پیشنهادی برای page.tsx:")
            print('''
export default function Home() {
  return (
    <main className="min-h-screen bg-slate-900 text-white p-8" dir="rtl">
      <header className="text-center mb-12">
        <h1 className="text-5xl font-bold mb-4 text-cyan-400">🌍 Econojin</h1>
        <p className="text-xl text-slate-300">ابرپروژه خدمات جامع رایگان</p>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-7xl mx-auto">
        {[
          {icon: "🌤️", title: "هواشناسی", desc: "پیش‌بینی و هشدارهای کشاورزی"},
          {icon: "💰", title: "حسابداری", desc: "مدیریت مالی شخصی و کسب‌وکار"},
          {icon: "🗺️", title: "GIS", desc: "نقشه‌کشی و تحلیل مکانی"},
          {icon: "🎓", title: "آموزش", desc: "کلاس‌ها و وبینارهای آنلاین"},
          {icon: "🧠", title: "روانشناسی", desc: "مشاوره و آزمون‌های آنلاین"},
          {icon: "🌱", title: "EcoCoin", desc: "ماینینگ سبز و پاداش"},
        ].map((m, i) => (
          <div key={i} className="p-6 bg-slate-800 rounded-xl hover:bg-slate-700 transition cursor-pointer">
            <h3 className="text-xl font-bold mb-2">{m.icon} {m.title}</h3>
            <p className="text-slate-400">{m.desc}</p>
          </div>
        ))}
      </div>
    </main>
  )
}
            '''.strip())

def run_all_checks():
    """اجرای تمام بررسی‌ها"""
    print("🔍 Econojin Frontend Health Check")
    print("=" * 50)
    
    checks = [
        ("Node.js Version", check_node_version),
        ("npm Packages", check_npm_packages),
        ("App Router Structure", check_app_router_structure),
        ("Page Exports", check_page_exports),
        ("Layout.tsx", check_layout_tsx),
        ("node_modules", check_node_modules),
        ("Next Config", check_next_config),
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
        print("🎉 فرانت‌اند آماده اجراست!")
        print(f"\n🚀 برای اجرا:")
        print(f"   cd {WEB}")
        print("   npm run dev")
        print("\n🔗 سپس در مرورگر: http://localhost:3000")
        return 0
    else:
        suggest_fixes()
        print("\n⚠️ برخی مشکلات نیاز به رفع دارند")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_checks())