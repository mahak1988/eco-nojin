import sys
from pathlib import Path

print("=" * 60)
print("🔍 بررسی سریع سلامت پروژه")
print("=" * 60)

# بررسی importهای کلیدی
modules_to_check = [
    "structlog",
    "geoalchemy2",
    "rioxarray",
    "cdsapi",
    "prometheus_client",
]

print("\n📦 پکیج‌های نصب شده:")
for mod in modules_to_check:
    try:
        __import__(mod)
        print(f"  ✅ {mod}")
    except ImportError:
        print(f"  ❌ {mod} (نصب نشده)")

# بررسی aquacrop
print("\n🌾 وضعیت AquaCrop:")
try:
    from aquacrop import AquaCropOS

    print("  ✅ AquaCrop نصب شده (نسخه واقعی)")
except ImportError:
    try:
        from core.gaia.aquacrop_fallback import AquaCropOS

        print("  ⚠️ AquaCrop نصب نشده، اما fallback فعال است")
    except ImportError:
        print("  ❌ هیچ راه‌حلی برای AquaCrop وجود ندارد")

# بررسی ساختار پروژه
print("\n📁 پوشه‌های اصلی:")
main_dirs = ["backend", "frontend", "core", "scripts", "tests", "apps"]
for d in main_dirs:
    path = Path(d)
    if path.exists():
        py_count = len(list(path.rglob("*.py")))
        print(f"  📂 {d}/ ({py_count} فایل پایتون)")
    else:
        print(f"  ❌ {d}/ (یافت نشد)")

print("\n" + "=" * 60)
