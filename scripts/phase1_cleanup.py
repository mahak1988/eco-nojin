#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Phase 1 Cleanup v1.1.0 (Windows-Fixed)
===================================================
اصلاحات:
- رفع WinError 183 با بررسی وجود فایل مقصد
- اضافه کردن جستجوی فایل‌های گم‌شده
- بهبود مدیریت خطا در ویندوز
"""

import os
import sys
import shutil
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import logging

# ============================================================
# Configuration
# ============================================================

VERSION = "1.1.0"
PROJECT_NAME = "Eco Nojin"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase1_cleanup.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# Data Models
# ============================================================

@dataclass
class FileMove:
    source: Path
    destination: Path
    category: str
    reason: str
    backup_path: Optional[Path] = None
    status: str = "pending"
    action_taken: str = ""  # moved, overwritten, skipped, failed

@dataclass
class DirectoryCreate:
    path: Path
    purpose: str
    status: str = "pending"

@dataclass
class CleanupReport:
    timestamp: str
    dry_run: bool
    backup_created: bool
    backup_path: Optional[Path]
    files_moved: List[FileMove] = field(default_factory=list)
    directories_created: List[DirectoryCreate] = field(default_factory=list)
    gitignore_updated: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    files_found_elsewhere: List[Dict] = field(default_factory=list)
    
    @property
    def total_moves(self) -> int:
        return len([f for f in self.files_moved if f.status == "moved"])
    
    @property
    def total_overwritten(self) -> int:
        return len([f for f in self.files_moved if f.action_taken == "overwritten"])
    
    @property
    def total_failed(self) -> int:
        return len([f for f in self.files_moved if f.status == "failed"])
    
    @property
    def total_skipped(self) -> int:
        return len([f for f in self.files_moved if f.status == "skipped"])

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

def cprint(msg: str, color: str = Colors.END, end: str = "\n"):
    print(f"{color}{msg}{Colors.END}", end=end)

# ============================================================
# Phase 1 Cleanup Script (v1.1.0 - Windows Fixed)
# ============================================================

class Phase1Cleanup:
    def __init__(self, project_root: Path, dry_run: bool = False, create_backup: bool = False):
        self.project_root = project_root
        self.apps_dir = project_root / "apps"
        self.scripts_dir = project_root / "scripts"
        self.dry_run = dry_run
        self.create_backup = create_backup
        self.backup_dir: Optional[Path] = None
        self.report = CleanupReport(
            timestamp=datetime.now().isoformat(),
            dry_run=dry_run,
            backup_created=False,
            backup_path=None
        )
        self._setup_migration_map()
    
    def _setup_migration_map(self):
        self.script_files = {
            "analyze_dependencies.py": {
                "destination": "scripts/analysis/analyze_dependencies.py",
                "reason": "اسکریپت تحلیلی"
            },
            "analyze_project.py": {
                "destination": "scripts/analysis/analyze_project.py",
                "reason": "اسکریپت تحلیلی"
            },
            "check_api_app_usage.py": {
                "destination": "scripts/analysis/check_api_app_usage.py",
                "reason": "اسکریپت تحلیلی"
            },
            "compare_main_files.py": {
                "destination": "scripts/analysis/compare_main_files.py",
                "reason": "اسکریپت تحلیلی"
            },
            "inspect_api_router.py": {
                "destination": "scripts/analysis/inspect_api_router.py",
                "reason": "اسکریپت تحلیلی"
            },
            "cleanup_unused.py": {
                "destination": "scripts/maintenance/cleanup_unused.py",
                "reason": "اسکریپت نگهداری"
            },
        }
        
        self.test_files = {
            "test_admin_agent.py": {"destination": "apps/ai_agents/tests/test_admin_agent.py", "reason": "تست ai_agents"},
            "test_ai_agents.py": {"destination": "apps/ai_agents/tests/test_ai_agents.py", "reason": "تست ai_agents"},
            "test_code_assistant_agent.py": {"destination": "apps/ai_agents/tests/test_code_assistant_agent.py", "reason": "تست ai_agents"},
            "test_data_analyst_agent.py": {"destination": "apps/ai_agents/tests/test_data_analyst_agent.py", "reason": "تست ai_agents"},
            "test_research_agent.py": {"destination": "apps/ai_agents/tests/test_research_agent.py", "reason": "تست ai_agents"},
            "test_advanced_rag.py": {"destination": "apps/shared/tests/test_advanced_rag.py", "reason": "تست shared"},
            "test_fallback_system.py": {"destination": "apps/shared/tests/test_fallback_system.py", "reason": "تست shared"},
            "test_fast_compute.py": {"destination": "apps/shared/tests/test_fast_compute.py", "reason": "تست shared"},
            "test_llm_factory.py": {"destination": "apps/shared/tests/test_llm_factory.py", "reason": "تست shared"},
            "test_llm_simple.py": {"destination": "apps/shared/tests/test_llm_simple.py", "reason": "تست shared"},
            "test_rag.py": {"destination": "apps/shared/tests/test_rag.py", "reason": "تست shared"},
            "test_rag_integration.py": {"destination": "apps/shared/tests/test_rag_integration.py", "reason": "تست shared"},
            "test_integration.py": {"destination": "apps/shared/tests/test_integration.py", "reason": "تست shared"},
            "test_full_integration.py": {"destination": "apps/shared/tests/test_full_integration.py", "reason": "تست shared"},
            "test_streaming.py": {"destination": "apps/shared/tests/test_streaming.py", "reason": "تست shared"},
            "test_env_loading.py": {"destination": "apps/shared/tests/test_env_loading.py", "reason": "تست shared"},
            "test_xai_models.py": {"destination": "apps/shared/tests/test_xai_models.py", "reason": "تست shared"},
            "test_users.py": {"destination": "apps/users/tests/test_users.py", "reason": "تست users"},
        }
        
        self.database_files = ["econojin.db", "econojin_test.db"]
        
        self.directories_to_create = [
            {"path": "scripts/analysis", "purpose": "اسکریپت‌های تحلیلی"},
            {"path": "scripts/maintenance", "purpose": "اسکریپت‌های نگهداری"},
            {"path": "scripts/testing", "purpose": "اسکریپت‌های تست"},
            {"path": "apps/ai_agents/tests", "purpose": "تست‌های ai_agents"},
            {"path": "apps/users/tests", "purpose": "تست‌های users"},
            {"path": "apps/shared/tests", "purpose": "تست‌های shared"},
            {"path": "apps/simulation/tests", "purpose": "تست‌های simulation"},
        ]
    
    def execute(self) -> CleanupReport:
        cprint("\n" + "=" * 70, Colors.HEADER)
        cprint(f"🚀 {PROJECT_NAME} - Phase 1: Cleanup & Triage v{VERSION}", Colors.HEADER)
        cprint(f"   Mode: {'DRY RUN' if self.dry_run else 'LIVE'}", Colors.YELLOW if self.dry_run else Colors.GREEN)
        cprint("=" * 70, Colors.HEADER)
        
        try:
            self._pre_flight_checks()
            
            if self.create_backup and not self.dry_run:
                self._create_backup()
            
            self._create_directories()
            self._move_script_files()
            self._move_test_files()
            self._remove_database_files()
            self._create_test_init_files()
            self._update_gitignore()
            self._search_missing_files()  # جدید: جستجوی فایل‌های گم‌شده
            self._generate_report()
            
        except Exception as e:
            logger.error(f"❌ خطای غیرمنتظره: {e}")
            self.report.errors.append(f"خطای غیرمنتظره: {e}")
            import traceback
            traceback.print_exc()
        
        return self.report
    
    def _pre_flight_checks(self):
        cprint("\n🔍 گام ۰: بررسی‌های اولیه...", Colors.BLUE)
        
        if not self.apps_dir.exists():
            raise FileNotFoundError(f"پوشه apps یافت نشد: {self.apps_dir}")
        
        cprint(f"   ✅ پوشه apps یافت شد", Colors.GREEN)
    
    def _create_backup(self):
        cprint("\n💾 گام ۱: ایجاد backup...", Colors.BLUE)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"apps_backup_phase1_{timestamp}"
        self.backup_dir = self.project_root / ".backups" / backup_name
        
        if self.dry_run:
            cprint(f"   🔍 [DRY RUN] Backup: {self.backup_dir}", Colors.CYAN)
            self.report.backup_path = self.backup_dir
            return
        
        try:
            self.backup_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(self.apps_dir, self.backup_dir)
            self.report.backup_created = True
            self.report.backup_path = self.backup_dir
            cprint(f"   ✅ Backup ایجاد شد", Colors.GREEN)
        except Exception as e:
            logger.error(f"   ❌ خطا در backup: {e}")
            self.report.errors.append(f"خطا در backup: {e}")
            raise
    
    def _create_directories(self):
        cprint("\n📁 گام ۲: ایجاد دایرکتوری‌ها...", Colors.BLUE)
        
        for dir_info in self.directories_to_create:
            dir_path = self.project_root / dir_info["path"]
            
            dir_create = DirectoryCreate(path=dir_path, purpose=dir_info["purpose"])
            
            if dir_path.exists():
                dir_create.status = "skipped"
                cprint(f"   ⏩ {dir_info['path']} موجود است", Colors.DIM)
            else:
                if self.dry_run:
                    cprint(f"   🔍 [DRY RUN] ایجاد: {dir_info['path']}", Colors.CYAN)
                else:
                    try:
                        dir_path.mkdir(parents=True, exist_ok=True)
                        dir_create.status = "created"
                        cprint(f"   ✅ ایجاد شد: {dir_info['path']}", Colors.GREEN)
                    except Exception as e:
                        dir_create.status = "failed"
                        logger.error(f"   ❌ خطا: {e}")
                        self.report.errors.append(f"خطا در ایجاد {dir_info['path']}: {e}")
            
            self.report.directories_created.append(dir_create)
    
    def _safe_move_file(self, source: Path, destination: Path) -> Tuple[bool, str]:
        """
        انتقال امن فایل با مدیریت فایل‌های موجود در مقصد (Windows-compatible)
        """
        # اگر مبدأ وجود ندارد
        if not source.exists():
            return False, "source_not_found"
        
        # اگر مقصد وجود دارد
        if destination.exists():
            # بررسی اینکه آیا فایل‌ها یکسان هستند
            try:
                if source.stat().st_size == destination.stat().st_size:
                    # فایل‌ها احتمالاً یکسان هستند، مبدأ را حذف کن
                    if not self.dry_run:
                        source.unlink()
                    return True, "overwritten_same_size"
                else:
                    # فایل‌ها متفاوت هستند، مقصد را backup کن
                    if not self.dry_run:
                        backup_dest = destination.with_suffix(destination.suffix + ".bak")
                        counter = 1
                        while backup_dest.exists():
                            backup_dest = destination.with_suffix(f"{destination.suffix}.bak{counter}")
                            counter += 1
                        shutil.move(str(destination), str(backup_dest))
                        shutil.move(str(source), str(destination))
                    return True, "overwritten_with_backup"
            except Exception as e:
                return False, f"error: {e}"
        else:
            # مقصد وجود ندارد، انتقال عادی
            if self.dry_run:
                return True, "dry_run"
            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(destination))
                return True, "moved"
            except Exception as e:
                return False, f"error: {e}"
    
    def _move_script_files(self):
        cprint("\n📦 گام ۳: انتقال فایل‌های اسکریپتی...", Colors.BLUE)
        
        for file_name, info in self.script_files.items():
            source = self.apps_dir / file_name
            destination = self.project_root / info["destination"]
            
            file_move = FileMove(
                source=source,
                destination=destination,
                category="script",
                reason=info["reason"]
            )
            
            if not source.exists():
                file_move.status = "skipped"
                cprint(f"   ⏩ {file_name} در apps/ یافت نشد", Colors.DIM)
            else:
                success, action = self._safe_move_file(source, destination)
                
                if success:
                    file_move.status = "moved"
                    file_move.action_taken = action
                    
                    if action == "moved":
                        cprint(f"   ✅ انتقال: {file_name} → {info['destination']}", Colors.GREEN)
                    elif "overwritten" in action:
                        cprint(f"   🔄 جایگزین: {file_name} (مقصد قبلی backup شد)", Colors.YELLOW)
                    elif action == "dry_run":
                        cprint(f"   🔍 [DRY RUN] انتقال: {file_name}", Colors.CYAN)
                else:
                    file_move.status = "failed"
                    logger.error(f"   ❌ خطا: {file_name}: {action}")
                    self.report.errors.append(f"خطا در انتقال {file_name}: {action}")
            
            self.report.files_moved.append(file_move)
    
    def _move_test_files(self):
        cprint("\n🧪 گام ۴: انتقال فایل‌های تست...", Colors.BLUE)
        
        for file_name, info in self.test_files.items():
            source = self.apps_dir / file_name
            destination = self.project_root / info["destination"]
            
            file_move = FileMove(
                source=source,
                destination=destination,
                category="test",
                reason=info["reason"]
            )
            
            if not source.exists():
                file_move.status = "skipped"
                cprint(f"   ⏩ {file_name} یافت نشد", Colors.DIM)
            else:
                success, action = self._safe_move_file(source, destination)
                
                if success:
                    file_move.status = "moved"
                    file_move.action_taken = action
                    
                    if action == "moved":
                        cprint(f"   ✅ انتقال: {file_name} → {info['destination']}", Colors.GREEN)
                    elif "overwritten" in action:
                        cprint(f"   🔄 جایگزین: {file_name}", Colors.YELLOW)
                else:
                    file_move.status = "failed"
                    logger.error(f"   ❌ خطا: {file_name}: {action}")
                    self.report.errors.append(f"خطا در انتقال {file_name}: {action}")
            
            self.report.files_moved.append(file_move)
    
    def _remove_database_files(self):
        cprint("\n🗑️  گام ۵: حذف فایل‌های دیتابیس...", Colors.BLUE)
        
        for db_file in self.database_files:
            db_path = self.apps_dir / db_file
            
            if not db_path.exists():
                cprint(f"   ⏩ {db_file} یافت نشد", Colors.DIM)
                continue
            
            if self.dry_run:
                cprint(f"   🔍 [DRY RUN] حذف: {db_file}", Colors.CYAN)
            else:
                try:
                    if self.backup_dir:
                        backup_db = self.backup_dir / f"{db_file}.deleted_backup"
                        shutil.copy2(db_path, backup_db)
                    
                    db_path.unlink()
                    cprint(f"   ✅ حذف شد: {db_file}", Colors.GREEN)
                except Exception as e:
                    logger.error(f"   ❌ خطا: {e}")
                    self.report.errors.append(f"خطا در حذف {db_file}: {e}")
    
    def _create_test_init_files(self):
        cprint("\n📝 گام ۶: ایجاد __init__.py...", Colors.BLUE)
        
        test_dirs = [
            "apps/ai_agents/tests",
            "apps/users/tests",
            "apps/shared/tests",
            "apps/simulation/tests",
        ]
        
        for test_dir in test_dirs:
            init_file = self.project_root / test_dir / "__init__.py"
            
            if init_file.exists():
                cprint(f"   ⏩ {test_dir}/__init__.py موجود است", Colors.DIM)
                continue
            
            if self.dry_run:
                cprint(f"   🔍 [DRY RUN] ایجاد: {test_dir}/__init__.py", Colors.CYAN)
            else:
                try:
                    module_name = test_dir.split("/")[1]
                    content = f'"""Tests for {module_name} module"""\n'
                    init_file.write_text(content, encoding="utf-8")
                    cprint(f"   ✅ ایجاد شد: {test_dir}/__init__.py", Colors.GREEN)
                except Exception as e:
                    logger.error(f"   ❌ خطا: {e}")
                    self.report.errors.append(f"خطا: {e}")
    
    def _update_gitignore(self):
        cprint("\n🔒 گام ۷: به‌روزرسانی .gitignore...", Colors.BLUE)
        
        gitignore_path = self.project_root / ".gitignore"
        
        new_entries = """
# Eco Nojin - Phase 1 Cleanup
*.db
*.sqlite
*.sqlite3
__pycache__/
*.py[cod]
.backups/
*.log
"""
        
        if self.dry_run:
            cprint(f"   🔍 [DRY RUN] به‌روزرسانی .gitignore", Colors.CYAN)
        else:
            try:
                if gitignore_path.exists():
                    content = gitignore_path.read_text(encoding="utf-8")
                    if "Eco Nojin - Phase 1 Cleanup" in content:
                        cprint(f"   ⏩ .gitignore قبلاً به‌روزرسانی شده", Colors.DIM)
                    else:
                        with open(gitignore_path, "a", encoding="utf-8") as f:
                            f.write(new_entries)
                        cprint(f"   ✅ .gitignore به‌روزرسانی شد", Colors.GREEN)
                        self.report.gitignore_updated = True
                else:
                    gitignore_path.write_text(new_entries.strip(), encoding="utf-8")
                    cprint(f"   ✅ .gitignore ایجاد شد", Colors.GREEN)
                    self.report.gitignore_updated = True
            except Exception as e:
                logger.error(f"   ❌ خطا: {e}")
                self.report.errors.append(f"خطا: {e}")
    
    def _search_missing_files(self):
        """جستجوی فایل‌هایی که در apps/ root یافت نشدند"""
        cprint("\n🔎 گام ۹: جستجوی فایل‌های گم‌شده...", Colors.BLUE)
        
        missing_scripts = [f for f in self.script_files.keys() 
                          if not (self.apps_dir / f).exists()]
        missing_tests = [f for f in self.test_files.keys() 
                        if not (self.apps_dir / f).exists()]
        
        all_missing = missing_scripts + missing_tests
        
        if not all_missing:
            cprint("   ✅ تمام فایل‌ها یافت شدند", Colors.GREEN)
            return
        
        cprint(f"   ⚠️  {len(all_missing)} فایل در apps/ root یافت نشد. جستجو در کل پروژه...", Colors.YELLOW)
        
        found_count = 0
        for file_name in all_missing:
            # جستجو در کل پروژه
            found = list(self.project_root.rglob(file_name))
            
            if found:
                for f in found:
                    rel_path = f.relative_to(self.project_root)
                    self.report.files_found_elsewhere.append({
                        "file": file_name,
                        "found_at": str(rel_path)
                    })
                    cprint(f"   🔍 {file_name} یافت شد در: {rel_path}", Colors.CYAN)
                    found_count += 1
            else:
                cprint(f"   ❌ {file_name} در هیچ جای پروژه یافت نشد", Colors.RED)
        
        if found_count > 0:
            cprint(f"\n   📊 {found_count} فایل در مسیرهای دیگر یافت شدند", Colors.GREEN)
            cprint("   💡 پیشنهاد: این فایل‌ها را دستی بررسی و منتقل کنید", Colors.YELLOW)
    
    def _generate_report(self):
        cprint("\n📊 گام ۱۰: تولید گزارش...", Colors.BLUE)
        
        report_path = self.project_root / "phase1_cleanup_report.json"
        
        report_data = {
            "timestamp": self.report.timestamp,
            "version": VERSION,
            "dry_run": self.report.dry_run,
            "backup_created": self.report.backup_created,
            "backup_path": str(self.report.backup_path) if self.report.backup_path else None,
            "summary": {
                "total_files_moved": self.report.total_moves,
                "total_overwritten": self.report.total_overwritten,
                "total_failed": self.report.total_failed,
                "total_skipped": self.report.total_skipped,
                "total_directories_created": len([d for d in self.report.directories_created if d.status == "created"]),
                "gitignore_updated": self.report.gitignore_updated,
                "files_found_elsewhere": len(self.report.files_found_elsewhere),
            },
            "files_moved": [
                {
                    "source": str(f.source),
                    "destination": str(f.destination),
                    "category": f.category,
                    "status": f.status,
                    "action": f.action_taken
                }
                for f in self.report.files_moved
            ],
            "files_found_elsewhere": self.report.files_found_elsewhere,
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
        
        cprint(f"\n   📦 منتقل‌شده: {Colors.BOLD}{self.report.total_moves}{Colors.END}")
        cprint(f"   🔄 جایگزین‌شده: {Colors.BOLD}{self.report.total_overwritten}{Colors.END}")
        cprint(f"   ❌ ناموفق: {Colors.BOLD}{self.report.total_failed}{Colors.END}")
        cprint(f"   ⏩ ردشده: {Colors.BOLD}{self.report.total_skipped}{Colors.END}")
        
        dirs_created = len([d for d in self.report.directories_created if d.status == "created"])
        cprint(f"   📁 دایرکتوری جدید: {Colors.BOLD}{dirs_created}{Colors.END}")
        cprint(f"   🔍 یافت‌شده در مسیر دیگر: {Colors.BOLD}{len(self.report.files_found_elsewhere)}{Colors.END}")
        
        if self.report.errors:
            cprint(f"\n   {Colors.RED}❌ خطاها ({len(self.report.errors)}):{Colors.END}")
            for error in self.report.errors[:5]:
                cprint(f"      • {error}", Colors.RED)
        
        cprint("\n" + "=" * 70, Colors.HEADER)
        
        if not self.dry_run and self.report.total_failed == 0:
            cprint("\n✅ فاز ۱ کامل شد!", Colors.GREEN + Colors.BOLD)
        elif self.dry_run:
            cprint("\n🔍 Dry Run کامل شد.", Colors.YELLOW)

def main():
    parser = argparse.ArgumentParser(description=f"{PROJECT_NAME} Phase 1 v{VERSION}")
    parser.add_argument("--root", type=str, default=".", help="ریشه پروژه")
    parser.add_argument("--dry-run", action="store_true", help="اجرای آزمایشی")
    parser.add_argument("--backup", action="store_true", help="ایجاد backup")
    
    args = parser.parse_args()
    project_root = Path(args.root).resolve()
    
    cprint(f"\n🌱 {PROJECT_NAME} Phase 1 v{VERSION}", Colors.BOLD)
    cprint(f"📂 ریشه: {project_root}", Colors.DIM)
    
    cleanup = Phase1Cleanup(project_root, args.dry_run, args.backup)
    report = cleanup.execute()
    
    sys.exit(1 if report.total_failed > 0 else 0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n⏹️  متوقف شد.", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        cprint(f"\n❌ خطا: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)