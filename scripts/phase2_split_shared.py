#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Phase 2: Split Shared Module
=========================================
شکستن ماژول shared به ۴ زیرماژول مستقل

ساختار جدید:
- shared-core: database, schemas, utils (بدون وابستگی AI)
- shared-ai: llm, rag, tools, agents
- shared-sim: compute, scientific models
- shared-knowledge: knowledge management

نحوه اجرا:
    # Dry-run
    python scripts/maintenance/phase2_split_shared.py --dry-run
    
    # اجرای واقعی
    python scripts/maintenance/phase2_split_shared.py
    
    # با backup
    python scripts/maintenance/phase2_split_shared.py --backup
    
    # Rollback
    python scripts/maintenance/phase2_split_shared.py --rollback

نویسنده: Eco Nojin Team
نسخه: 2.0.0
تاریخ: 2026-07-12
"""

import os
import sys
import shutil
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import logging

# ============================================================
# Configuration
# ============================================================

VERSION = "2.0.0"
PROJECT_NAME = "Eco Nojin"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase2_split_shared.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# Data Models
# ============================================================

@dataclass
class FileMigration:
    source: Path
    destination: Path
    target_module: str
    reason: str
    status: str = "pending"
    imports_updated: int = 0

@dataclass
class ImportUpdate:
    file: Path
    old_import: str
    new_import: str
    status: str = "pending"

@dataclass
class Phase2Report:
    timestamp: str
    dry_run: bool
    backup_created: bool
    backup_path: Optional[Path]
    files_migrated: List[FileMigration] = field(default_factory=list)
    imports_updated: List[ImportUpdate] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    dependency_graph: Dict[str, Set[str]] = field(default_factory=dict)
    
    @property
    def total_migrated(self) -> int:
        return len([f for f in self.files_migrated if f.status == "migrated"])
    
    @property
    def total_failed(self) -> int:
        return len([f for f in self.files_migrated if f.status == "failed"])
    
    @property
    def total_imports_updated(self) -> int:
        return len([i for i in self.imports_updated if i.status == "updated"])

# ============================================================
# Terminal Colors
# ============================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

def cprint(msg: str, color: str = Colors.END):
    print(f"{color}{msg}{Colors.END}")

# ============================================================
# Phase 2 Script
# ============================================================

class Phase2SplitShared:
    def __init__(self, project_root: Path, dry_run: bool = False, create_backup: bool = False):
        self.project_root = project_root
        self.apps_dir = project_root / "apps"
        self.shared_dir = self.apps_dir / "shared"
        self.dry_run = dry_run
        self.create_backup = create_backup
        self.backup_dir: Optional[Path] = None
        self.report = Phase2Report(
            timestamp=datetime.now().isoformat(),
            dry_run=dry_run,
            backup_created=False,
            backup_path=None
        )
        
        # نقشه انتقال فایل‌ها
        self.migration_map: Dict[str, str] = {}
        self.import_map: Dict[str, str] = {}
        
        self._build_migration_map()
    
    def _build_migration_map(self):
        """ساخت نقشه انتقال فایل‌ها بر اساس اسکن ساختار فعلی"""
        
        if not self.shared_dir.exists():
            logger.error(f"پوشه shared یافت نشد: {self.shared_dir}")
            return
        
        # اسکن ساختار فعلی shared
        for py_file in self.shared_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            rel_path = py_file.relative_to(self.shared_dir)
            rel_str = str(rel_path).replace("\\", "/")
            
            # تعیین ماژول مقصد بر اساس مسیر
            target_module = self._determine_target_module(rel_str, py_file)
            
            if target_module:
                dest_path = f"apps/{target_module}/{rel_str}"
                self.migration_map[rel_str] = dest_path
                
                # ساخت نقشه import
                old_import = f"apps.shared.{rel_str.replace('/', '.').replace('.py', '')}"
                new_import = f"apps.{target_module}.{rel_str.replace('/', '.').replace('.py', '')}"
                self.import_map[old_import] = new_import
    
    def _determine_target_module(self, rel_path: str, file_path: Path) -> Optional[str]:
        """تعیین ماژول مقصد بر اساس مسیر و محتوای فایل"""
        
        # بر اساس مسیر
        if rel_path.startswith("database/") or rel_path.startswith("schemas/") or rel_path.startswith("utils/"):
            return "shared-core"
        
        if rel_path.startswith("ai/") or rel_path.startswith("tools/"):
            return "shared-ai"
        
        if rel_path.startswith("knowledge/"):
            return "shared-knowledge"
        
        if rel_path.startswith("compute/") or rel_path.startswith("simulation/"):
            return "shared-sim"
        
        # بر اساس محتوا (برای فایل‌های ریشه)
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # فایل‌های AI
            if any(keyword in content for keyword in ["langchain", "llm", "agent", "tool", "rag", "embedding"]):
                return "shared-ai"
            
            # فایل‌های محاسباتی
            if any(keyword in content for keyword in ["numpy", "scipy", "numba", "compute", "simulation"]):
                return "shared-sim"
            
            # فایل‌های دانش
            if any(keyword in content for keyword in ["knowledge", "knowledge_base"]):
                return "shared-knowledge"
            
            # پیش‌فرض: shared-core
            return "shared-core"
            
        except Exception as e:
            logger.warning(f"خطا در خواندن {file_path}: {e}")
            return "shared-core"
    
    def execute(self) -> Phase2Report:
        cprint("\n" + "=" * 70, Colors.HEADER)
        cprint(f"🚀 {PROJECT_NAME} - Phase 2: Split Shared Module v{VERSION}", Colors.HEADER)
        cprint(f"   Mode: {'DRY RUN' if self.dry_run else 'LIVE'}", Colors.YELLOW if self.dry_run else Colors.GREEN)
        cprint("=" * 70, Colors.HEADER)
        
        try:
            # گام ۰: بررسی‌های اولیه
            self._pre_flight_checks()
            
            # گام ۱: ایجاد backup
            if self.create_backup and not self.dry_run:
                self._create_backup()
            
            # گام ۲: تحلیل وابستگی‌ها
            self._analyze_dependencies()
            
            # گام ۳: ایجاد ساختار جدید
            self._create_new_structure()
            
            # گام ۴: انتقال فایل‌ها
            self._migrate_files()
            
            # گام ۵: به‌روزرسانی importها
            self._update_imports()
            
            # گام ۶: ایجاد __init__.py
            self._create_init_files()
            
            # گام ۷: حذف پوشه shared قدیمی
            self._remove_old_shared()
            
            # گام ۸: تست صحت تغییرات
            self._test_changes()
            
            # گام ۹: تولید گزارش
            self._generate_report()
            
        except Exception as e:
            logger.error(f"❌ خطای غیرمنتظره: {e}")
            self.report.errors.append(f"خطای غیرمنتظره: {e}")
            import traceback
            traceback.print_exc()
        
        return self.report
    
    def _pre_flight_checks(self):
        cprint("\n🔍 گام ۰: بررسی‌های اولیه...", Colors.BLUE)
        
        if not self.shared_dir.exists():
            raise FileNotFoundError(f"پوشه shared یافت نشد: {self.shared_dir}")
        
        file_count = len(list(self.shared_dir.rglob("*.py")))
        cprint(f"   ✅ پوشه shared یافت شد: {file_count} فایل Python", Colors.GREEN)
        
        # بررسی نقشه انتقال
        if not self.migration_map:
            cprint("   ⚠️  نقشه انتقال خالی است", Colors.YELLOW)
        else:
            cprint(f"   ✅ {len(self.migration_map)} فایل برای انتقال شناسایی شد", Colors.GREEN)
    
    def _create_backup(self):
        cprint("\n💾 گام ۱: ایجاد backup...", Colors.BLUE)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"shared_backup_phase2_{timestamp}"
        self.backup_dir = self.project_root / ".backups" / backup_name
        
        if self.dry_run:
            cprint(f"   🔍 [DRY RUN] Backup: {self.backup_dir}", Colors.CYAN)
            self.report.backup_path = self.backup_dir
            return
        
        try:
            self.backup_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(self.shared_dir, self.backup_dir)
            self.report.backup_created = True
            self.report.backup_path = self.backup_dir
            cprint(f"   ✅ Backup ایجاد شد", Colors.GREEN)
        except Exception as e:
            logger.error(f"   ❌ خطا: {e}")
            self.report.errors.append(f"خطا در backup: {e}")
            raise
    
    def _analyze_dependencies(self):
        cprint("\n🕸️  گام ۲: تحلیل وابستگی‌ها...", Colors.BLUE)
        
        # اسکن تمام فایل‌های Python برای یافتن importهای shared
        dependency_graph = defaultdict(set)
        
        for py_file in self.apps_dir.rglob("*.py"):
            if "shared" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8")
                
                # یافتن importهای shared
                imports = re.findall(r'from\s+(apps\.shared\.[^\s]+)', content)
                imports += re.findall(r'import\s+(apps\.shared\.[^\s]+)', content)
                
                for imp in imports:
                    module_name = imp.split('.')[1] if len(imp.split('.')) > 1 else "unknown"
                    dependency_graph[module_name].add(str(py_file.relative_to(self.project_root)))
                
            except Exception:
                continue
        
        self.report.dependency_graph = dict(dependency_graph)
        
        cprint(f"   ✅ {len(dependency_graph)} ماژول وابسته به shared شناسایی شد", Colors.GREEN)
        for module, files in sorted(dependency_graph.items()):
            cprint(f"      • {module}: {len(files)} فایل", Colors.DIM)
    
    def _create_new_structure(self):
        cprint("\n🏗️  گام ۳: ایجاد ساختار جدید...", Colors.BLUE)
        
        new_modules = ["shared-core", "shared-ai", "shared-sim", "shared-knowledge"]
        
        for module in new_modules:
            module_path = self.apps_dir / module
            if self.dry_run:
                cprint(f"   🔍 [DRY RUN] ایجاد: {module}", Colors.CYAN)
            else:
                module_path.mkdir(parents=True, exist_ok=True)
                cprint(f"   ✅ ایجاد شد: {module}", Colors.GREEN)
    
    def _migrate_files(self):
        cprint("\n📦 گام ۴: انتقال فایل‌ها...", Colors.BLUE)
        
        for source_rel, dest_rel in self.migration_map.items():
            source = self.shared_dir / source_rel
            destination = self.project_root / dest_rel
            
            migration = FileMigration(
                source=source,
                destination=destination,
                target_module=dest_rel.split('/')[1],
                reason=f"انتقال به {dest_rel.split('/')[1]}"
            )
            
            if not source.exists():
                migration.status = "skipped"
                cprint(f"   ⏩ {source_rel} یافت نشد", Colors.DIM)
            else:
                if self.dry_run:
                    cprint(f"   🔍 [DRY RUN] انتقال: {source_rel} → {dest_rel}", Colors.CYAN)
                    migration.status = "pending"
                else:
                    try:
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(source), str(destination))
                        migration.status = "migrated"
                        cprint(f"   ✅ {source_rel} → {dest_rel}", Colors.GREEN)
                    except Exception as e:
                        migration.status = "failed"
                        logger.error(f"   ❌ خطا: {e}")
                        self.report.errors.append(f"خطا در انتقال {source_rel}: {e}")
            
            self.report.files_migrated.append(migration)
    
    def _update_imports(self):
        cprint("\n🔄 گام ۵: به‌روزرسانی importها...", Colors.BLUE)
        
        if not self.import_map:
            cprint("   ⚠️  نقشه import خالی است", Colors.YELLOW)
            return
        
        # اسکن تمام فایل‌های Python
        for py_file in self.apps_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                original_content = content
                
                # جایگزینی importها
                for old_import, new_import in self.import_map.items():
                    if old_import in content:
                        content = content.replace(old_import, new_import)
                        
                        import_update = ImportUpdate(
                            file=py_file,
                            old_import=old_import,
                            new_import=new_import,
                            status="updated"
                        )
                        self.report.imports_updated.append(import_update)
                
                # نوشتن در صورت تغییر
                if content != original_content:
                    if not self.dry_run:
                        py_file.write_text(content, encoding="utf-8")
                    cprint(f"   ✅ {py_file.relative_to(self.project_root)}", Colors.GREEN)
                
            except Exception as e:
                logger.error(f"   ❌ خطا در {py_file}: {e}")
                self.report.errors.append(f"خطا در به‌روزرسانی {py_file}: {e}")
        
        cprint(f"   ✅ {len(self.report.imports_updated)} import به‌روزرسانی شد", Colors.GREEN)
    
    def _create_init_files(self):
        cprint("\n📝 گام ۶: ایجاد __init__.py...", Colors.BLUE)
        
        new_modules = ["shared-core", "shared-ai", "shared-sim", "shared-knowledge"]
        
        for module in new_modules:
            init_file = self.apps_dir / module / "__init__.py"
            
            if self.dry_run:
                cprint(f"   🔍 [DRY RUN] ایجاد: {module}/__init__.py", Colors.CYAN)
            else:
                if not init_file.exists():
                    content = f'"""Eco Nojin - {module} module"""\n\n__version__ = "1.0.0"\n'
                    init_file.write_text(content, encoding="utf-8")
                    cprint(f"   ✅ {module}/__init__.py", Colors.GREEN)
                else:
                    cprint(f"   ⏩ {module}/__init__.py موجود است", Colors.DIM)
    
    def _remove_old_shared(self):
        cprint("\n🗑️  گام ۷: حذف پوشه shared قدیمی...", Colors.BLUE)
        
        if self.dry_run:
            cprint(f"   🔍 [DRY RUN] حذف: {self.shared_dir}", Colors.CYAN)
        else:
            try:
                # بررسی اینکه پوشه خالی است
                remaining_files = list(self.shared_dir.rglob("*"))
                if remaining_files:
                    cprint(f"   ⚠️  {len(remaining_files)} فایل باقی‌مانده در shared", Colors.YELLOW)
                    for f in remaining_files[:5]:
                        cprint(f"      • {f.relative_to(self.shared_dir)}", Colors.DIM)
                else:
                    shutil.rmtree(self.shared_dir)
                    cprint(f"   ✅ پوشه shared حذف شد", Colors.GREEN)
            except Exception as e:
                logger.error(f"   ❌ خطا: {e}")
                self.report.errors.append(f"خطا در حذف shared: {e}")
    
    def _test_changes(self):
        cprint("\n🧪 گام ۸: تست صحت تغییرات...", Colors.BLUE)
        
        if self.dry_run:
            cprint("   🔍 [DRY RUN] تست اجرا نمی‌شود", Colors.CYAN)
            return
        
        # تست importهای اصلی
        test_imports = [
            "from apps.shared_core.database.session import get_db",
            "from apps.shared_ai.llm.llm_factory import get_llm",
            "from apps.main import app",
        ]
        
        for test_import in test_imports:
            try:
                exec(test_import)
                cprint(f"   ✅ {test_import}", Colors.GREEN)
            except Exception as e:
                cprint(f"   ❌ {test_import}: {e}", Colors.RED)
                self.report.errors.append(f"تست import ناموفق: {test_import}")
    
    def _generate_report(self):
        cprint("\n📊 گام ۹: تولید گزارش...", Colors.BLUE)
        
        report_path = self.project_root / "phase2_split_shared_report.json"
        
        report_data = {
            "timestamp": self.report.timestamp,
            "version": VERSION,
            "dry_run": self.report.dry_run,
            "backup_created": self.report.backup_created,
            "backup_path": str(self.report.backup_path) if self.report.backup_path else None,
            "summary": {
                "total_files_migrated": self.report.total_migrated,
                "total_failed": self.report.total_failed,
                "total_imports_updated": self.report.total_imports_updated,
                "modules_created": 4,
            },
            "files_migrated": [
                {
                    "source": str(f.source),
                    "destination": str(f.destination),
                    "target_module": f.target_module,
                    "status": f.status
                }
                for f in self.report.files_migrated
            ],
            "imports_updated": len(self.report.imports_updated),
            "dependency_graph": {k: list(v) for k, v in self.report.dependency_graph.items()},
            "errors": self.report.errors,
            "warnings": self.report.warnings
        }
        
        if not self.dry_run:
            report_path.write_text(
                json.dumps(report_data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            cprint(f"   ✅ گزارش: {report_path}", Colors.GREEN)
        
        # چاپ خلاصه
        cprint("\n" + "=" * 70, Colors.HEADER)
        cprint("📈 خلاصه عملیات", Colors.HEADER)
        cprint("=" * 70, Colors.HEADER)
        
        cprint(f"\n   📦 فایل‌های منتقل‌شده: {Colors.BOLD}{self.report.total_migrated}{Colors.END}")
        cprint(f"   ❌ ناموفق: {Colors.BOLD}{self.report.total_failed}{Colors.END}")
        cprint(f"   🔄 Importهای به‌روزرسانی‌شده: {Colors.BOLD}{self.report.total_imports_updated}{Colors.END}")
        
        if self.report.errors:
            cprint(f"\n   {Colors.RED}❌ خطاها ({len(self.report.errors)}):{Colors.END}")
            for error in self.report.errors[:5]:
                cprint(f"      • {error}", Colors.RED)
        
        cprint("\n" + "=" * 70, Colors.HEADER)
        
        if not self.dry_run and self.report.total_failed == 0:
            cprint("\n✅ فاز ۲ کامل شد!", Colors.GREEN + Colors.BOLD)
            cprint("\n📌 گام‌های بعدی:", Colors.BLUE)
            cprint("   1. بررسی گزارش: phase2_split_shared_report.json", Colors.DIM)
            cprint("   2. اجرای تست‌ها: pytest apps/*/tests/", Colors.DIM)
            cprint("   3. Commit: git add . && git commit -m 'Phase 2: Split shared'", Colors.DIM)
            cprint("   4. شروع فاز ۳: بازسازماندهی web", Colors.DIM)
    
    def rollback(self):
        cprint("\n" + "=" * 70, Colors.HEADER)
        cprint("⏪ Rollback - بازگشت به حالت قبل", Colors.HEADER)
        cprint("=" * 70, Colors.HEADER)
        
        if not self.backup_dir or not self.backup_dir.exists():
            cprint("\n❌ Backup یافت نشد", Colors.RED)
            return
        
        cprint(f"\n💾 Backup: {self.backup_dir}", Colors.GREEN)
        
        confirm = input("\nآیا مطمئن هستید؟ (yes/no): ")
        if confirm.lower() != "yes":
            cprint("\n❌ لغو شد", Colors.RED)
            return
        
        try:
            # حذف ماژول‌های جدید
            for module in ["shared-core", "shared-ai", "shared-sim", "shared-knowledge"]:
                module_path = self.apps_dir / module
                if module_path.exists():
                    shutil.rmtree(module_path)
                    cprint(f"   🗑️  حذف شد: {module}", Colors.YELLOW)
            
            # بازیابی shared
            shutil.copytree(self.backup_dir, self.shared_dir)
            cprint(f"   ✅ shared بازیابی شد", Colors.GREEN)
            
            cprint("\n✅ Rollback کامل شد!", Colors.GREEN + Colors.BOLD)
            
        except Exception as e:
            logger.error(f"❌ خطا: {e}")
            cprint(f"\n❌ خطا: {e}", Colors.RED)

# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description=f"{PROJECT_NAME} Phase 2 v{VERSION}")
    parser.add_argument("--root", type=str, default=".")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--backup", action="store_true")
    parser.add_argument("--rollback", action="store_true")
    
    args = parser.parse_args()
    project_root = Path(args.root).resolve()
    
    cprint(f"\n🌱 {PROJECT_NAME} Phase 2 v{VERSION}", Colors.BOLD)
    cprint(f"📂 ریشه: {project_root}", Colors.DIM)
    
    phase2 = Phase2SplitShared(project_root, args.dry_run, args.backup)
    
    if args.rollback:
        phase2.rollback()
    else:
        report = phase2.execute()
        sys.exit(1 if report.total_failed > 0 else 0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n⏹️  متوقف شد", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        cprint(f"\n❌ خطا: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)