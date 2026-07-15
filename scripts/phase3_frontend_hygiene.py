#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Phase 3: Frontend Code Hygiene
===========================================
بهداشت کد فرانت‌اند: حذف کد مرده، اصلاح hooks، ادغام دایرکتوری‌ها

نحوه اجرا:
    python scripts/maintenance/phase3_frontend_hygiene.py --dry-run
    python scripts/maintenance/phase3_frontend_hygiene.py
    python scripts/maintenance/phase3_frontend_hygiene.py --backup

نویسنده: Eco Nojin Team
نسخه: 3.0.0
"""

import sys
import re
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import logging

# ============================================================
# Configuration
# ============================================================

VERSION = "3.0.0"
PROJECT_NAME = "Eco Nojin"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase3_frontend_hygiene.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# Data Models
# ============================================================

@dataclass
class HygieneAction:
    type: str  # delete_file, fix_useeffect, merge_dir, add_test
    target: str
    description: str
    status: str = "pending"  # pending, done, failed, skipped
    details: str = ""

@dataclass
class Phase3Report:
    timestamp: str
    dry_run: bool
    actions: List[HygieneAction] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def total_done(self) -> int:
        return len([a for a in self.actions if a.status == "done"])
    
    @property
    def total_failed(self) -> int:
        return len([a for a in self.actions if a.status == "failed"])

# ============================================================
# Colors
# ============================================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

def cprint(msg: str, color: str = Colors.END):
    print(f"{color}{msg}{Colors.END}")

# ============================================================
# Phase 3 Hygiene Script
# ============================================================

class FrontendHygiene:
    def __init__(self, project_root: Path, dry_run: bool = False, backup: bool = False):
        self.project_root = project_root
        self.web_dir = project_root / "apps" / "web"
        self.src_dir = self.web_dir / "src"
        self.dry_run = dry_run
        self.backup = backup
        self.backup_dir: Optional[Path] = None
        self.report = Phase3Report(
            timestamp=datetime.now().isoformat(),
            dry_run=dry_run
        )
    
    def execute(self) -> Phase3Report:
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint(f"🧹 {PROJECT_NAME} - Phase 3: Frontend Code Hygiene v{VERSION}", Colors.BOLD)
        cprint(f"   Mode: {'DRY RUN' if self.dry_run else 'LIVE'}", Colors.YELLOW if self.dry_run else Colors.GREEN)
        cprint("=" * 70, Colors.BOLD)
        
        try:
            # گام ۰: بررسی‌های اولیه
            self._pre_flight_checks()
            
            # گام ۱: ایجاد backup
            if self.backup and not self.dry_run:
                self._create_backup()
            
            # گام ۲: حذف کد مرده
            self._remove_dead_code()
            
            # گام ۳: اصلاح useEffect
            self._fix_use_effect()
            
            # گام ۴: ادغام دایرکتوری‌های کوچک
            self._merge_small_directories()
            
            # گام ۵: تولید گزارش
            self._generate_report()
            
        except Exception as e:
            logger.error(f"❌ خطا: {e}")
            self.report.errors.append(str(e))
            import traceback
            traceback.print_exc()
        
        return self.report
    
    def _pre_flight_checks(self):
        cprint("\n🔍 گام ۰: بررسی‌های اولیه...", Colors.BLUE)
        
        if not self.src_dir.exists():
            raise FileNotFoundError(f"src/ یافت نشد: {self.src_dir}")
        
        file_count = len(list(self.src_dir.rglob("*.tsx"))) + len(list(self.src_dir.rglob("*.ts")))
        cprint(f"   ✅ src/ یافت شد: {file_count} فایل TypeScript", Colors.GREEN)
    
    def _create_backup(self):
        cprint("\n💾 گام ۱: ایجاد backup...", Colors.BLUE)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.project_root / ".backups" / f"web_backup_phase3_{timestamp}"
        
        try:
            self.backup_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(self.web_dir, self.backup_dir)
            cprint(f"   ✅ Backup ایجاد شد: {self.backup_dir}", Colors.GREEN)
        except Exception as e:
            cprint(f"   ❌ خطا: {e}", Colors.RED)
            self.report.errors.append(f"Backup error: {e}")
    
    def _remove_dead_code(self):
        cprint("\n🗑️  گام ۲: حذف کد مرده...", Colors.BLUE)
        
        # لیست فایل‌های مرده (بر اساس گزارش تحلیل)
        dead_files = [
            "src/vite-env.d.ts",  # خالی
            "src/pages/Chat.tsx",  # unused
            "src/pages/SimulationRunner.tsx",  # unused
            "src/services/blockchain.ts",  # unused
            "src/pages/Hydrology/HydrologyDashboard.tsx",  # unused
            "src/pages/Simulators/Simulators.tsx",  # unused
        ]
        
        # توجه: main.tsx را حذف نمی‌کنیم چون entry point است
        # اما بررسی می‌کنیم که واقعاً unused است یا نه
        
        for file_rel in dead_files:
            file_path = self.web_dir / file_rel
            
            action = HygieneAction(
                type="delete_file",
                target=str(file_path),
                description=f"حذف فایل مرده: {file_rel}"
            )
            
            if not file_path.exists():
                action.status = "skipped"
                cprint(f"   ⏩ {file_rel} یافت نشد", Colors.DIM)
            else:
                # بررسی اینکه واقعاً import نشده
                if self._is_file_imported(file_path):
                    action.status = "skipped"
                    cprint(f"   ⚠️  {file_rel} هنوز import شده - حذف نشد", Colors.YELLOW)
                else:
                    if self.dry_run:
                        cprint(f"   🔍 [DRY RUN] حذف: {file_rel}", Colors.CYAN)
                        action.status = "pending"
                    else:
                        try:
                            file_path.unlink()
                            action.status = "done"
                            cprint(f"   ✅ حذف شد: {file_rel}", Colors.GREEN)
                            
                            # حذف دایرکتوری خالی والد
                            self._remove_empty_parent_dirs(file_path.parent)
                        except Exception as e:
                            action.status = "failed"
                            cprint(f"   ❌ خطا: {e}", Colors.RED)
                            self.report.errors.append(f"Delete error: {e}")
            
            self.report.actions.append(action)
    
    def _is_file_imported(self, file_path: Path) -> bool:
        """بررسی اینکه آیا فایلی توسط فایل دیگری import شده"""
        file_stem = file_path.stem
        
        for ts_file in self.src_dir.rglob("*.ts*"):
            if ts_file == file_path:
                continue
            
            try:
                content = ts_file.read_text(encoding="utf-8")
                # جستجوی importهای مختلف
                patterns = [
                    rf"from\s+['\"].*{file_stem}['\"]",
                    rf"import\(['\"].*{file_stem}['\"]\)",
                    rf"['\"].*{file_stem}['\"]",
                ]
                for pattern in patterns:
                    if re.search(pattern, content):
                        return True
            except Exception:
                continue
        
        return False
    
    def _remove_empty_parent_dirs(self, dir_path: Path):
        """حذف دایرکتوری‌های خالی والد"""
        try:
            while dir_path != self.src_dir and dir_path.exists():
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    cprint(f"   🗑️  دایرکتوری خالی حذف شد: {dir_path.relative_to(self.web_dir)}", Colors.DIM)
                    dir_path = dir_path.parent
                else:
                    break
        except Exception:
            pass
    
    def _fix_use_effect(self):
        cprint("\n🔧 گام ۳: اصلاح useEffect...", Colors.BLUE)
        
        # فایل‌های با useEffect مشکل‌دار
        problem_files = [
            "src/hooks/useApi.tsx",
            "src/pages/Chat.tsx",  # اگر حذف نشده باشد
        ]
        
        for file_rel in problem_files:
            file_path = self.web_dir / file_rel
            
            if not file_path.exists():
                cprint(f"   ⏩ {file_rel} یافت نشد", Colors.DIM)
                continue
            
            action = HygieneAction(
                type="fix_useeffect",
                target=str(file_path),
                description=f"اصلاح useEffect در: {file_rel}"
            )
            
            try:
                content = file_path.read_text(encoding="utf-8")
                original = content
                
                # الگوی useEffect بدون dependency
                # useEffect(() => { ... })  →  useEffect(() => { ... }, [])
                pattern = r"(useEffect\s*\(\s*\(\)\s*=>\s*\{[^}]*\}\s*)(?!\s*,\s*\[)(?!\s*\))"
                
                # بررسی ساده‌تر: اگر useEffect بدون [] وجود دارد
                if "useEffect(" in content and "], [])" not in content and "], [" not in content:
                    # افزودن [] به useEffect
                    content = re.sub(
                        r"(useEffect\s*\(\s*\(\)\s*=>\s*\{)",
                        r"\1",
                        content
                    )
                    
                    # راه‌حل بهتر: افزودن dependency array خالی
                    content = re.sub(
                        r"(useEffect\s*\([^)]*\)\s*)(?!\s*,\s*\[)",
                        r"\1, [])",
                        content
                    )
                
                if content != original:
                    if self.dry_run:
                        cprint(f"   🔍 [DRY RUN] اصلاح: {file_rel}", Colors.CYAN)
                        action.status = "pending"
                    else:
                        file_path.write_text(content, encoding="utf-8")
                        action.status = "done"
                        cprint(f"   ✅ اصلاح شد: {file_rel}", Colors.GREEN)
                else:
                    action.status = "skipped"
                    cprint(f"   ⏩ {file_rel} نیاز به اصلاح نداشت", Colors.DIM)
            
            except Exception as e:
                action.status = "failed"
                cprint(f"   ❌ خطا در {file_rel}: {e}", Colors.RED)
                self.report.errors.append(f"Fix error: {e}")
            
            self.report.actions.append(action)
    
    def _merge_small_directories(self):
        cprint("\n📁 گام ۴: ادغام دایرکتوری‌های کوچک...", Colors.BLUE)
        
        # شناسایی دایرکتوری‌های با فقط ۱ فایل
        small_dirs = []
        
        for dir_path in self.src_dir.rglob("*"):
            if not dir_path.is_dir():
                continue
            
            # شمارش فایل‌های کد
            code_files = [f for f in dir_path.iterdir() 
                         if f.is_file() and f.suffix in [".ts", ".tsx"]]
            
            if len(code_files) == 1 and dir_path != self.src_dir:
                small_dirs.append((dir_path, code_files[0]))
        
        cprint(f"   ℹ️  {len(small_dirs)} دایرکتوری با ۱ فایل شناسایی شد", Colors.CYAN)
        
        # ادغام دایرکتوری‌های بسیار کوچک (فقط برای نمایش - ادغام واقعی نیاز به بررسی دستی دارد)
        for dir_path, single_file in small_dirs[:5]:  # فقط ۵ تا
            rel_path = dir_path.relative_to(self.web_dir)
            cprint(f"   📂 {rel_path}/ ({single_file.name})", Colors.DIM)
            
            action = HygieneAction(
                type="merge_dir",
                target=str(dir_path),
                description=f"دایرکتوری کوچک: {rel_path}"
            )
            action.status = "skipped"  # ادغام واقعی نیاز به بررسی دستی دارد
            self.report.actions.append(action)
        
        cprint(f"   💡 برای ادغام واقعی، بررسی دستی لازم است", Colors.YELLOW)
    
    def _generate_report(self):
        cprint("\n📊 گام ۵: تولید گزارش...", Colors.BLUE)
        
        report_path = self.project_root / "phase3_hygiene_report.json"
        
        report_data = {
            "timestamp": self.report.timestamp,
            "version": VERSION,
            "dry_run": self.report.dry_run,
            "summary": {
                "total_actions": len(self.report.actions),
                "done": self.report.total_done,
                "failed": self.report.total_failed,
                "skipped": len([a for a in self.report.actions if a.status == "skipped"]),
            },
            "actions": [
                {
                    "type": a.type,
                    "target": a.target,
                    "description": a.description,
                    "status": a.status
                }
                for a in self.report.actions
            ],
            "errors": self.report.errors
        }
        
        if not self.dry_run:
            report_path.write_text(
                json.dumps(report_data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            cprint(f"   ✅ گزارش: {report_path}", Colors.GREEN)
        
        # چاپ خلاصه
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint("📈 خلاصه عملیات", Colors.BOLD)
        cprint("=" * 70, Colors.BOLD)
        
        cprint(f"\n   ✅ انجام‌شده: {Colors.GREEN}{self.report.total_done}{Colors.END}")
        cprint(f"   ❌ ناموفق: {Colors.RED}{self.report.total_failed}{Colors.END}")
        cprint(f"   ⏩ ردشده: {Colors.YELLOW}{len([a for a in self.report.actions if a.status == 'skipped'])}{Colors.END}")
        
        if self.report.errors:
            cprint(f"\n   {Colors.RED}❌ خطاها:{Colors.END}")
            for e in self.report.errors:
                cprint(f"      • {e}", Colors.RED)
        
        cprint("\n" + "=" * 70, Colors.BOLD)
        
        if self.report.total_failed == 0:
            cprint("\n✅ فاز ۳ با موفقیت کامل شد!", Colors.GREEN + Colors.BOLD)
            cprint("\n📌 گام‌های بعدی:", Colors.BLUE)
            cprint("   1. اجرای build: cd apps/web && pnpm build")
            cprint("   2. اجرای سرور: pnpm dev")
            cprint("   3. Commit: git add . && git commit -m 'phase-3: hygiene'")

# ============================================================
# Main
# ============================================================

def find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "apps").exists():
            return current
        current = current.parent
    return Path.cwd()

def main():
    import argparse
    parser = argparse.ArgumentParser(description=f"{PROJECT_NAME} Phase 3 v{VERSION}")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--backup", action="store_true")
    
    args = parser.parse_args()
    project_root = find_project_root()
    
    cprint(f"\n🌱 {PROJECT_NAME} Phase 3 v{VERSION}", Colors.BOLD)
    cprint(f"📂 ریشه: {project_root}", Colors.DIM)
    
    hygiene = FrontendHygiene(project_root, args.dry_run, args.backup)
    report = hygiene.execute()
    
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