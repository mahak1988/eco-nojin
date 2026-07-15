#!/usr/bin/env python3
"""
اسکریپت اصلاح ساختار domains/
حل مشکلات ایجاد شده توسط اسکریپت قبلی
"""
import os
import shutil
from pathlib import Path

API_ROOT = Path(r"D:\econojin.com\api")
DOMAINS = API_ROOT / "domains"

def fix_structure():
    print("=" * 70)
    print("🔧 اصلاح ساختار domains/")
    print("=" * 70)
    
    # ۱. حذف فایل‌های __pycache__
    print("\n🗑️  حذف فایل‌های __pycache__...")
    pycache_files = [
        DOMAINS / "__pycache__" / "__init__.cpython-313.pyc",
        DOMAINS / "soil" / "__pycache__" / "models.cpython-313.pyc",
        DOMAINS / "soil" / "__pycache__" / "models.cpython-314.pyc",
        DOMAINS / "water" / "__pycache__" / "__init__.cpython-313.pyc",
        DOMAINS / "soil" / "__pycache__" / "__init__.cpython-313.pyc",
    ]
    
    for f in pycache_files:
        if f.exists():
            f.unlink()
            print(f"   ✅ حذف: {f}")
    
    # حذف پوشه‌های __pycache__ خالی
    for pycache in DOMAINS.rglob("__pycache__"):
        if pycache.is_dir() and not any(pycache.iterdir()):
            pycache.rmdir()
            print(f"   ✅ حذف پوشه خالی: {pycache}")
    
    # ۲. انتقال فایل‌های scientific_core به پوشه scientific_core
    print("\n📂 انتقال فایل‌های scientific_core...")
    scientific_core_files = [
        "carbon.py", "crops.py", "databases.py", "drought.py",
        "erosion.py", "hydrology.py", "indices.py", "router.py",
        "soil_water.py", "__init__.py"
    ]
    
    scientific_core_dir = DOMAINS / "scientific_core"
    scientific_core_dir.mkdir(exist_ok=True)
    
    for filename in scientific_core_files:
        src = DOMAINS / filename
        if src.exists() and src.is_file():
            dst = scientific_core_dir / filename
            if dst.exists():
                print(f"   ⚠️  تداخل: {filename} (backup شد)")
                dst.rename(dst.with_suffix('.py.backup'))
            shutil.move(str(src), str(dst))
            print(f"   ✅ انتقال: {filename} → scientific_core/")
    
    # ۳. انتقال فایل‌های سرویس به پوشه‌های مربوطه
    print("\n📂 انتقال فایل‌های سرویس...")
    service_files = {
        "carbon_calculator.py": "carbon/",
        "drought_core.py": "drought/",
        "drought_databases.py": "drought/",
        "early_warning_engine.py": "iot/",
        "eco_miner.py": "ecocoin/",
        "llm.py": "ai/",
        "orchestration_service.py": "simulation/",
        "rothc_full.py": "carbon/",
        "simulation_engine.py": "simulation/",
        "sms.py": "notification/",
        "soil_water_calculator.py": "soil_water/",
        "soil_water_core.py": "soil_water/",
        "weather_service.py": "weather/",
    }
    
    for filename, target_dir in service_files.items():
        src = DOMAINS / filename
        if src.exists():
            target_path = DOMAINS / target_dir
            target_path.mkdir(exist_ok=True)
            dst = target_path / filename
            shutil.move(str(src), str(dst))
            print(f"   ✅ انتقال: {filename} → {target_dir}")
    
    # ۴. حل تداخل router.py
    print("\n🔧 حل تداخل router.py...")
    router_file = DOMAINS / "router.py"
    if router_file.exists():
        # انتقال به scientific_core
        dst = scientific_core_dir / "router.py"
        if dst.exists():
            dst.rename(dst.with_suffix('.py.backup'))
        shutil.move(str(router_file), str(dst))
        print(f"   ✅ انتقال: router.py → scientific_core/")
    
    # ۵. حذف پوشه‌های خالی
    print("\n🗑️  حذف پوشه‌های خالی...")
    for item in DOMAINS.iterdir():
        if item.is_dir() and not any(item.iterdir()):
            item.rmdir()
            print(f"   ✅ حذف پوشه خالی: {item.name}")
    
    print("\n" + "=" * 70)
    print("✅ اصلاح ساختار تکمیل شد!")
    print("=" * 70)

if __name__ == "__main__":
    fix_structure()