#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔗 Unify Frontends - یکپارچه‌سازی ساختارهای فرانت‌اند
ادغام فایل‌های منحصر به فرد از frontend/ و web/ به apps/web/
"""
import shutil
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

ROOT = Path(__file__).parent.resolve()
PRIMARY = ROOT / "apps" / "web"       # ساختار اصلی (فعال)
LEGACY1 = ROOT / "frontend"           # قدیمی
LEGACY2 = ROOT / "web"                # متوسط
ARCHIVE_DIR = ROOT / "_legacy_frontends_archive"

# فایل‌هایی که باید نادیده گرفته شوند (تکراری یا کش)
IGNORE_PATTERNS = {
    "node_modules", ".next", "dist", "build", ".git",
    "package-lock.json", "pnpm-lock.yaml", ".pnpm-store",
    "__pycache__", "*.pyc", ".DS_Store", "Thumbs.db",
    "next-env.d.ts", ".turbo"
}

# فایل‌های پیکربندی که نباید منتقل شوند (apps/web مالک است)
CONFIG_FILES = {
    "package.json", "next.config.js", "next.config.mjs",
    "tsconfig.json", "tailwind.config.js", "tailwind.config.ts",
    "postcss.config.js", ".env", ".env.example", ".env.local",
    "middleware.ts", "vercel.json", "vitest.config.ts",
    "playwright.config.ts"
}


def should_ignore(path: Path) -> bool:
    """بررسی اینکه آیا فایل باید نادیده گرفته شود"""
    for pattern in IGNORE_PATTERNS:
        if pattern.startswith("*"):
            if path.suffix == pattern[1:]:
                return True
        elif pattern in path.parts:
            return True
        elif path.name == pattern:
            return True
    return False


def get_file_signature(path: Path) -> str:
    """ایجاد امضای فایل بر اساس مسیر نسبی"""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:1000]
    except:
        return ""


def analyze_directory(base_dir: Path, name: str) -> dict:
    """آنالیز یک دایرکتوری فرانت‌اند"""
    stats = {
        "name": name,
        "path": base_dir,
        "total_files": 0,
        "total_size_mb": 0,
        "file_types": defaultdict(int),
        "unique_files": [],
        "duplicate_files": [],
        "config_files": [],
    }
    
    if not base_dir.exists():
        return stats
    
    for path in base_dir.rglob("*"):
        if not path.is_file() or should_ignore(path):
            continue
        
        stats["total_files"] += 1
        stats["total_size_mb"] += path.stat().st_size / 1_048_576
        stats["file_types"][path.suffix or "no_ext"] += 1
        
        # دسته‌بندی فایل
        rel_path = path.relative_to(base_dir)
        
        if path.name in CONFIG_FILES:
            stats["config_files"].append(str(rel_path))
        else:
            # بررسی منحصر به فرد بودن
            target_path = PRIMARY / rel_path
            if target_path.exists():
                # مقایسه محتوا
                if get_file_signature(path) == get_file_signature(target_path):
                    stats["duplicate_files"].append(str(rel_path))
                else:
                    stats["unique_files"].append({
                        "path": str(rel_path),
                        "status": "conflict",
                        "note": "محتوای متفاوت"
                    })
            else:
                stats["unique_files"].append({
                    "path": str(rel_path),
                    "status": "new",
                    "note": "فایل جدید"
                })
    
    return stats


def phase_analyze():
    """فاز 1: آنالیز و نمایش گزارش"""
    print("\n" + "=" * 70)
    print("📊 PHASE 1: آنالیز ساختارهای فرانت‌اند")
    print("=" * 70)
    
    # آنالیز هر سه ساختار
    primary_stats = {
        "name": "apps/web (PRIMARY)",
        "total_files": sum(1 for p in PRIMARY.rglob("*") if p.is_file() and not should_ignore(p)),
        "total_size_mb": sum(p.stat().st_size for p in PRIMARY.rglob("*") if p.is_file() and not should_ignore(p)) / 1_048_576,
    }
    
    legacy1_stats = analyze_directory(LEGACY1, "frontend (LEGACY)")
    legacy2_stats = analyze_directory(LEGACY2, "web (LEGACY)")
    
    # نمایش گزارش
    print(f"\n📁 ساختار اصلی (فعال):")
    print(f"   📂 {PRIMARY.relative_to(ROOT)}")
    print(f"   📄 {primary_stats['total_files']} فایل | 💾 {primary_stats['total_size_mb']:.1f} MB")
    
    for stats in [legacy1_stats, legacy2_stats]:
        print(f"\n📁 {stats['name']}:")
        print(f"   📂 {stats['path'].relative_to(ROOT) if stats['path'].exists() else 'NOT FOUND'}")
        print(f"   📄 {stats['total_files']} فایل | 💾 {stats['total_size_mb']:.1f} MB")
        
        if stats['total_files'] > 0:
            print(f"   📊 انواع فایل:")
            for ext, count in sorted(stats['file_types'].items(), key=lambda x: -x[1])[:5]:
                print(f"      • {ext or 'no_ext'}: {count}")
            
            print(f"\n   🎯 فایل‌های منحصر به فرد: {len(stats['unique_files'])}")
            print(f"   🔄 فایل‌های تکراری: {len(stats['duplicate_files'])}")
            print(f"   ⚙️  فایل‌های پیکربندی: {len(stats['config_files'])}")
            
            # نمایش نمونه فایل‌های منحصر به فرد
            if stats['unique_files']:
                print(f"\n   📋 نمونه فایل‌های منحصر به فرد:")
                for item in stats['unique_files'][:10]:
                    path_str = item['path'] if isinstance(item, dict) else item
                    status = item.get('status', '') if isinstance(item, dict) else ''
                    icon = "🆕" if status == "new" else "⚠️"
                    print(f"      {icon} {path_str}")
                if len(stats['unique_files']) > 10:
                    print(f"      ... و {len(stats['unique_files']) - 10} فایل دیگر")
    
    # محاسبه فضای قابل آزادسازی
    total_legacy_size = legacy1_stats['total_size_mb'] + legacy2_stats['total_size_mb']
    print(f"\n💾 فضای قابل آزادسازی: ~{total_legacy_size:.1f} MB")
    
    return legacy1_stats, legacy2_stats


def archive_directory(source: Path, name: str) -> bool:
    """آرشیو کردن یک دایرکتوری"""
    if not source.exists():
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = ARCHIVE_DIR / f"{name}_{timestamp}"
    
    try:
        shutil.copytree(source, archive_path)
        print(f"   📦 آرشیو شد: {archive_path.relative_to(ROOT)}")
        return True
    except Exception as e:
        print(f"   ❌ خطا در آرشیو: {e}")
        return False


def transfer_unique_files(source: Path, stats: dict) -> int:
    """انتقال فایل‌های منحصر به فرد به ساختار اصلی"""
    transferred = 0
    
    for item in stats['unique_files']:
        rel_path = item['path'] if isinstance(item, dict) else item
        source_file = source / rel_path
        target_file = PRIMARY / rel_path
        
        if not source_file.exists():
            continue
        
        try:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            if target_file.exists():
                # فایل موجود است - ایجاد نسخه با پسوند .merged
                backup = target_file.with_suffix(target_file.suffix + ".legacy-backup")
                shutil.copy2(target_file, backup)
            
            shutil.copy2(source_file, target_file)
            transferred += 1
        except Exception as e:
            print(f"   ⚠️ خطا در انتقال {rel_path}: {e}")
    
    return transferred


def phase_execute(legacy1_stats, legacy2_stats):
    """فاز 2: اجرای یکپارچه‌سازی"""
    print("\n" + "=" * 70)
    print("⚙️  PHASE 2: اجرای یکپارچه‌سازی")
    print("=" * 70)
    
    # ایجاد پوشه آرشیو
    ARCHIVE_DIR.mkdir(exist_ok=True)
    
    total_transferred = 0
    
    # پردازش هر ساختار قدیمی
    for source, stats in [(LEGACY1, legacy1_stats), (LEGACY2, legacy2_stats)]:
        if not source.exists() or stats['total_files'] == 0:
            continue
        
        print(f"\n🔄 پردازش {stats['name']}...")
        
        # 1. انتقال فایل‌های منحصر به فرد
        print(f"   📤 انتقال فایل‌های منحصر به فرد...")
        transferred = transfer_unique_files(source, stats)
        print(f"   ✅ {transferred} فایل منتقل شد")
        total_transferred += transferred
        
        # 2. آرشیو کردن کل پوشه
        print(f"   📦 آرشیو کردن پوشه...")
        if archive_directory(source, source.name):
            # 3. حذف پوشه اصلی
            try:
                shutil.rmtree(source)
                print(f"   🗑️ حذف شد: {source.relative_to(ROOT)}")
            except Exception as e:
                print(f"   ⚠️ خطا در حذف: {e}")
    
    return total_transferred


def main():
    print("🔗 Unify Frontends - یکپارچه‌سازی ساختارهای فرانت‌اند")
    print("=" * 70)
    print(f"📁 ساختار اصلی: {PRIMARY.relative_to(ROOT)}")
    print(f"📁 ساختارهای قدیمی: {LEGACY1.name}/, {LEGACY2.name}/")
    print("=" * 70)
    
    # فاز 1: آنالیز
    legacy1_stats, legacy2_stats = phase_analyze()
    
    # بررسی اینکه آیا کاری برای انجام وجود دارد
    total_unique = len(legacy1_stats['unique_files']) + len(legacy2_stats['unique_files'])
    total_legacy = legacy1_stats['total_files'] + legacy2_stats['total_files']
    
    if total_legacy == 0:
        print("\n✅ هیچ ساختار قدیمی یافت نشد. پروژه یکپارچه است!")
        return 0
    
    # فاز 2: تایید و اجرا
    print("\n" + "=" * 70)
    print("⚠️  اقدامات پیشنهادی:")
    print(f"   1. انتقال {total_unique} فایل منحصر به فرد به apps/web/")
    print(f"   2. آرشیو کردن frontend/ و web/")
    print(f"   3. حذف پوشه‌های قدیمی")
    print("=" * 70)
    
    confirm = input("\n   ادامه؟ (yes/no): ").strip().lower()
    if confirm != "yes":
        print("\n❌ لغو شد")
        return 0
    
    # اجرای فاز 2
    transferred = phase_execute(legacy1_stats, legacy2_stats)
    
    # گزارش نهایی
    print("\n" + "=" * 70)
    print("✅ یکپارچه‌سازی تکمیل شد!")
    print(f"\n📊 آمار:")
    print(f"   📤 فایل‌های منتقل‌شده: {transferred}")
    print(f"   📦 آرشیو: {ARCHIVE_DIR.relative_to(ROOT)}/")
    print(f"\n🎯 ساختار نهایی:")
    print(f"   📂 apps/web/        ← ساختار اصلی (یکپارچه)")
    print(f"   📂 _legacy_frontends_archive/  ← آرشیو")
    print(f"\n🚀 گام بعدی:")
    print(f"   1. بررسی apps/web/ برای اطمینان از صحت انتقال")
    print(f"   2. اجرای: cd apps/web && pnpm run dev -- -p 3001")
    print(f"   3. Commit: git add . && git commit -m 'refactor: unify frontend structure'")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())