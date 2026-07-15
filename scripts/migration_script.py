#!/usr/bin/env python3
"""
اسکریپت مهاجرت خودکار ساختار پروژه
مهاجرت از ساختار فعلی به Clean Architecture + DDD
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
import json


class MigrationManager:
    """مدیریت مهاجرت ساختار پروژه"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.api_root = project_root / "apps" / "api"
        self.backup_dir = project_root / ".migration_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.migration_log = []
        
        # نقشه مهاجرت: مسیر قدیمی -> مسیر جدید
        self.migration_map = {
            # انتقال domains به domain
            "domains/hydrology": "domain/hydrology",
            "domains/carbon": "domain/carbon",
            "domains/drought": "domain/drought",
            "domains/financial": "domain/financial",
            "domains/iot": "domain/iot",
            "domains/lms": "domain/lms",
            "domains/logframe": "domain/logframe",
            "domains/mrv": "domain/mrv",
            "domains/pilots": "domain/pilots",
            "domains/psychology": "domain/psychology",
            "domains/remote_sensing": "domain/remote_sensing",
            "domains/safeguards": "domain/safeguards",
            "domains/soil_water": "domain/soil_water",
            "domains/training": "domain/training",
            "domains/dashboard": "domain/dashboard",
            
            # انتقال modules به domain
            "modules/academy": "domain/academy",
            "modules/accounting": "domain/accounting",
            "modules/auth": "domain/auth",
            "modules/calendar": "domain/calendar",
            "modules/community": "domain/community",
            "modules/ecocoin": "domain/ecocoin",
            "modules/ecomining": "domain/ecomining",
            "modules/education": "domain/education",
            "modules/farmer": "domain/farmer",
            "modules/games": "domain/games",
            "modules/gis": "domain/gis",
            "modules/library": "domain/library",
            "modules/maintenance": "domain/maintenance",
            "modules/newsletter": "domain/newsletter",
            "modules/settings": "domain/settings",
            "modules/simulation": "domain/simulation",
            "modules/store": "domain/store",
            "modules/structures": "domain/structures",
            "modules/water": "domain/water",
            "modules/weather": "domain/weather",
            
            # انتقال routers به api/v1/endpoints
            "routers": "api/v1/endpoints",
            
            # انتقال services به infrastructure
            "services": "infrastructure/services",
            
            # انتقال scientific_core به domain
            "scientific_core": "domain/scientific",
        }
    
    def create_backup(self):
        """ایجاد backup از ساختار فعلی"""
        print(f"📦 ایجاد backup در: {self.backup_dir}")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # backup از apps/api
        api_backup = self.backup_dir / "apps" / "api"
        if self.api_root.exists():
            shutil.copytree(self.api_root, api_backup)
            print(f"✅ Backup از apps/api ایجاد شد")
    
    def create_new_structure(self):
        """ایجاد ساختار جدید"""
        print("\n🏗️ ایجاد ساختار جدید...")
        
        # ایجاد پوشه‌های اصلی
        new_dirs = [
            "app/core",
            "app/api/v1/endpoints",
            "app/domain",
            "app/infrastructure/repositories",
            "app/infrastructure/external_services",
        ]
        
        for dir_path in new_dirs:
            full_path = self.api_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ ایجاد: {dir_path}")
    
    def migrate_files(self):
        """انتقال فایل‌ها بر اساس نقشه مهاجرت"""
        print("\n📦 انتقال فایل‌ها...")
        
        for old_path, new_path in self.migration_map.items():
            old_full = self.api_root / old_path
            new_full = self.api_root / new_path
            
            if not old_full.exists():
                continue
            
            print(f"\n  📂 انتقال: {old_path} → {new_path}")
            
            if old_full.is_dir():
                # انتقال دایرکتوری
                self._migrate_directory(old_full, new_full)
            else:
                # انتقال فایل
                self._migrate_file(old_full, new_full)
    
    def _migrate_directory(self, src: Path, dst: Path):
        """انتقال دایرکتوری"""
        dst.mkdir(parents=True, exist_ok=True)
        
        for item in src.iterdir():
            dst_item = dst / item.name
            
            if item.is_dir():
                self._migrate_directory(item, dst_item)
            else:
                self._migrate_file(item, dst_item)
        
        # حذف دایرکتوری خالی
        try:
            shutil.rmtree(src)
            self.migration_log.append(f"✅ حذف دایرکتوری: {src.relative_to(self.api_root)}")
        except Exception as e:
            self.migration_log.append(f"⚠️ خطا در حذف {src}: {e}")
    
    def _migrate_file(self, src: Path, dst: Path):
        """انتقال فایل"""
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            self.migration_log.append(f"✅ انتقال: {src.relative_to(self.api_root)} → {dst.relative_to(self.api_root)}")
        except Exception as e:
            self.migration_log.append(f"⚠️ خطا در انتقال {src}: {e}")
    
    def update_imports(self):
        """به‌روزرسانی import ها در فایل‌های Python"""
        print("\n🔄 به‌روزرسانی import ها...")
        
        # نقشه به‌روزرسانی import ها
        import_map = {
            # domains -> domain
            "from apps.app.domains": "from apps.app.app.domain",
            "import apps.app.domains": "import apps.app.app.domain",
            
            # modules -> domain
            "from apps.app.modules": "from apps.app.app.domain",
            "import apps.app.modules": "import apps.app.app.domain",
            
            # routers -> api.v1.endpoints
            "from apps.app.routers": "from apps.app.app.api.v1.endpoints",
            "import apps.app.routers": "import apps.app.app.api.v1.endpoints",
            
            # services -> infrastructure
            "from apps.app.services": "from apps.app.app.infrastructure.services",
            "import apps.app.services": "import apps.app.app.infrastructure.services",
            
            # scientific_core -> domain.scientific
            "from apps.app.scientific_core": "from apps.app.app.domain.scientific",
            "import apps.app.scientific_core": "import apps.app.app.domain.scientific",
        }
        
        # پیدا کردن تمام فایل‌های Python
        py_files = list(self.api_root.rglob("*.py"))
        
        updated_count = 0
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # به‌روزرسانی import ها
                for old_import, new_import in import_map.items():
                    content = content.replace(old_import, new_import)
                
                # ذخیره در صورت تغییر
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    updated_count += 1
                    self.migration_log.append(f"✅ به‌روزرسانی import: {py_file.relative_to(self.api_root)}")
            
            except Exception as e:
                self.migration_log.append(f"⚠️ خطا در به‌روزرسانی {py_file}: {e}")
        
        print(f"  ✓ به‌روزرسانی {updated_count} فایل")
    
    def remove_empty_directories(self):
        """حذف دایرکتوری‌های خالی"""
        print("\n🧹 حذف دایرکتوری‌های خالی...")
        
        removed_count = 0
        for dirpath, dirnames, filenames in os.walk(self.api_root, topdown=False):
            if not os.listdir(dirpath):
                try:
                    os.rmdir(dirpath)
                    removed_count += 1
                    self.migration_log.append(f"✅ حذف دایرکتوری خالی: {Path(dirpath).relative_to(self.api_root)}")
                except Exception as e:
                    self.migration_log.append(f"⚠️ خطا در حذف {dirpath}: {e}")
        
        print(f"  ✓ حذف {removed_count} دایرکتوری خالی")
    
    def save_migration_log(self):
        """ذخیره لاگ مهاجرت"""
        log_file = self.backup_dir / "migration_log.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.migration_log))
        print(f"\n📝 لاگ مهاجرت ذخیره شد در: {log_file}")
    
    def run_migration(self, dry_run: bool = False):
        """اجرای کامل مهاجرت"""
        print("=" * 70)
        print("🚀 شروع مهاجرت ساختار پروژه")
        print("=" * 70)
        
        if dry_run:
            print("⚠️ حالت آزمایشی (Dry Run) - هیچ تغییری اعمال نمی‌شود")
        
        # ایجاد backup
        if not dry_run:
            self.create_backup()
        
        # ایجاد ساختار جدید
        if not dry_run:
            self.create_new_structure()
        
        # انتقال فایل‌ها
        self.migrate_files()
        
        # به‌روزرسانی import ها
        if not dry_run:
            self.update_imports()
        
        # حذف دایرکتوری‌های خالی
        if not dry_run:
            self.remove_empty_directories()
        
        # ذخیره لاگ
        if not dry_run:
            self.save_migration_log()
        
        print("\n" + "=" * 70)
        print("✅ مهاجرت با موفقیت انجام شد!")
        print("=" * 70)


def main():
    """تابع اصلی"""
    import argparse
    
    parser = argparse.ArgumentParser(description="مهاجرت ساختار پروژه به Clean Architecture")
    parser.add_argument("--dry-run", action="store_true", help="حالت آزمایشی بدون اعمال تغییرات")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).parent, help="مسیر ریشه پروژه")
    
    args = parser.parse_args()
    
    # ایجاد مدیر مهاجرت
    manager = MigrationManager(args.project_root)
    
    # اجرای مهاجرت
    manager.run_migration(dry_run=args.dry_run)


if __name__ == "__main__":
    main()