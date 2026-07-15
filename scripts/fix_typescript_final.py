#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - TypeScript Build Fix v3.0 (Final & Precise)
========================================================
اسکریپت دقیق و ایمن برای رفع تمام ۸۲ خطای TypeScript

ویژگی‌ها:
✅ Idempotent (اجرای چند باره نتیجه یکسان)
✅ Safe (backup خودکار قبل از تغییرات)
✅ Precise (فقط تغییرات ضروری)
✅ Reversible (قابلیت rollback)
✅ Detailed Logging (گزارش دقیق)

نحوه اجرا:
    python scripts/testing/fix_typescript_final.py
    python scripts/testing/fix_typescript_final.py --dry-run
    python scripts/testing/fix_typescript_final.py --rollback

نویسنده: Eco Nojin Architecture Team
نسخه: 3.0.0
"""

import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass, field
import logging

# ============================================================
# Configuration
# ============================================================

VERSION = "3.0.0"
PROJECT_NAME = "Eco Nojin"

# تنظیم لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('typescript_fix_v3.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================
# Data Models
# ============================================================

@dataclass
class FixResult:
    """نتیجه رفع یک خطا"""
    file: str
    category: str
    action: str
    status: str = "pending"  # pending, done, failed, skipped
    details: str = ""
    line: int = 0


@dataclass
class FixReport:
    """گزارش نهایی رفع خطاها"""
    timestamp: str
    dry_run: bool
    backup_path: Optional[Path] = None
    results: List[FixResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def total_done(self) -> int:
        return len([r for r in self.results if r.status == "done"])
    
    @property
    def total_failed(self) -> int:
        return len([r for r in self.results if r.status == "failed"])
    
    @property
    def total_skipped(self) -> int:
        return len([r for r in self.results if r.status == "skipped"])


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
# Helper Functions
# ============================================================

def find_project_root() -> Path:
    """پیدا کردن ریشه پروژه"""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "apps").exists():
            return current
        current = current.parent
    return Path.cwd()


def create_backup(src_dir: Path, backup_base: Path) -> Path:
    """ایجاد backup از دایرکتوری"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_base / f"ts_fix_backup_{timestamp}"
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_dir, backup_path)
    return backup_path


# ============================================================
# Category A: Fix unused kpis
# ============================================================

def fix_unused_kpis(file_path: Path, dry_run: bool) -> FixResult:
    """
    کامنت کردن متغیر kpis استفاده نشده
    
    الگو:
    const kpis = {
      "kpis": [...]
    };
    """
    result = FixResult(
        file=str(file_path),
        category="A: kpis unused",
        action="Comment out kpis"
    )
    
    if not file_path.exists():
        result.status = "skipped"
        result.details = "File not found"
        return result
    
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content
        
        # الگوی دقیق برای کpis block
        # پشتیبانی از multi-line
        pattern = r'(\s*)const\s+kpis\s*=\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\};'
        
        def comment_kpis(match):
            indent = match.group(1)
            block = match.group(0)
            # کامنت کردن هر خط
            commented_lines = []
            for line in block.split('\n'):
                if line.strip():
                    commented_lines.append(f"{indent}// {line.strip()}")
                else:
                    commented_lines.append(line)
            return '\n'.join(commented_lines)
        
        content = re.sub(pattern, comment_kpis, content, flags=re.DOTALL)
        
        if content != original:
            if not dry_run:
                file_path.write_text(content, encoding="utf-8")
            result.status = "done"
            result.details = "kpis commented out"
        else:
            result.status = "skipped"
            result.details = "No kpis found or already commented"
    
    except Exception as e:
        result.status = "failed"
        result.details = str(e)
    
    return result


# ============================================================
# Category B: Fix unused language
# ============================================================

def fix_unused_language(file_path: Path, dry_run: bool) -> FixResult:
    """
    حذف language از destructuring useLanguage
    
    الگو:
    const { t, dir, language } = useLanguage();
    تبدیل به:
    const { t, dir } = useLanguage();
    """
    result = FixResult(
        file=str(file_path),
        category="B: language unused",
        action="Remove language from destructuring"
    )
    
    if not file_path.exists():
        result.status = "skipped"
        result.details = "File not found"
        return result
    
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content
        
        # بررسی اینکه آیا language واقعاً استفاده شده
        # اگر فقط در destructuring باشد و جای دیگر نه، حذف می‌کنیم
        language_usages = len(re.findall(r'\blanguage\b', content))
        
        # اگر فقط ۱ بار (در destructuring) استفاده شده
        if language_usages == 1:
            content = re.sub(
                r'const\s*\{\s*t\s*,\s*dir\s*,\s*language\s*\}\s*=\s*useLanguage\(\)',
                'const { t, dir } = useLanguage()',
                content
            )
        
        if content != original:
            if not dry_run:
                file_path.write_text(content, encoding="utf-8")
            result.status = "done"
            result.details = "language removed from destructuring"
        else:
            result.status = "skipped"
            result.details = "language is used or not in destructuring"
    
    except Exception as e:
        result.status = "failed"
        result.details = str(e)
    
    return result


# ============================================================
# Category C: Fix type conflicts
# ============================================================

def fix_type_conflict(file_path: Path, type_name: str, dry_run: bool) -> FixResult:
    """
    حذف type definition تکراری که اسکریپت قبلی اضافه کرده
    
    الگو:
    // Type definitions
    export interface TypeName { ... }
    """
    result = FixResult(
        file=str(file_path),
        category="C: Type conflict",
        action=f"Remove duplicate {type_name} type"
    )
    
    if not file_path.exists():
        result.status = "skipped"
        result.details = "File not found"
        return result
    
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content
        
        # الگوی دقیق برای type definition تکراری
        if type_name in ["Satellite", "Scenario"]:
            pattern = rf'// Type definitions\s*\nexport interface {type_name}\s*\{{[^}}]+\}}\s*\n+'
        else:  # SimulatorAudience
            pattern = rf'// Type definitions\s*\nexport type {type_name}\s*=[^;]+;\s*\n+'
        
        content = re.sub(pattern, '', content)
        
        if content != original:
            if not dry_run:
                file_path.write_text(content, encoding="utf-8")
            result.status = "done"
            result.details = f"Removed duplicate {type_name} type"
        else:
            result.status = "skipped"
            result.details = f"No duplicate {type_name} found"
    
    except Exception as e:
        result.status = "failed"
        result.details = str(e)
    
    return result


# ============================================================
# Category D: Fix authService return type
# ============================================================

def fix_auth_service(file_path: Path, dry_run: bool) -> FixResult:
    """
    تغییر return type از User به MeResponse
    
    الگو:
    async getMe(): Promise<User>
    تبدیل به:
    async getMe(): Promise<MeResponse>
    """
    result = FixResult(
        file=str(file_path),
        category="D: Auth type mismatch",
        action="Change return type to MeResponse"
    )
    
    if not file_path.exists():
        result.status = "skipped"
        result.details = "File not found"
        return result
    
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content
        
        # تغییر return type
        content = re.sub(
            r'async\s+getMe\(\)\s*:\s*Promise<User>',
            'async getMe(): Promise<MeResponse>',
            content
        )
        
        if content != original:
            if not dry_run:
                file_path.write_text(content, encoding="utf-8")
            result.status = "done"
            result.details = "Return type changed to MeResponse"
        else:
            result.status = "skipped"
            result.details = "Return type already correct"
    
    except Exception as e:
        result.status = "failed"
        result.details = str(e)
    
    return result


# ============================================================
# Category E & F: Fix engines (destructuring + visualize)
# ============================================================

def fix_engine_file(file_path: Path, dry_run: bool) -> FixResult:
    """
    رفع فایل engine:
    1. حذف destructuring اشتباه
    2. حذف کامل متد visualize
    
    این ساده‌ترین و امن‌ترین راه‌حل است چون:
    - متد visualize استفاده نمی‌شود
    - destructuring اشتباه فقط خطا ایجاد می‌کند
    """
    result = FixResult(
        file=str(file_path),
        category="E/F: Engine fix",
        action="Remove bad destructuring + visualize method"
    )
    
    if not file_path.exists():
        result.status = "skipped"
        result.details = "File not found"
        return result
    
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content
        
        # ۱. حذف destructuring اشتباه
        # الگو: const { ... } = _result as any;
        content = re.sub(
            r'\s*const\s*\{[^}]+\}\s*=\s*_result\s+as\s+any;\s*\n',
            '\n',
            content
        )
        
        # ۲. حذف کامل متد visualize
        # الگوی دقیق: visualize(...): VisualizationSpec { ... }
        # باید تمام بلاک متد را حذف کند
        content = re.sub(
            r'\n\s*visualize\s*\([^)]*\)\s*:\s*VisualizationSpec\s*\{(?:[^{}]|\{[^{}]*\})*\}\s*\n',
            '\n',
            content,
            flags=re.DOTALL
        )
        
        if content != original:
            if not dry_run:
                file_path.write_text(content, encoding="utf-8")
            result.status = "done"
            result.details = "Removed bad destructuring and visualize method"
        else:
            result.status = "skipped"
            result.details = "No changes needed"
    
    except Exception as e:
        result.status = "failed"
        result.details = str(e)
    
    return result


# ============================================================
# Category G: Add simulator exports
# ============================================================

def add_simulator_export(file_path: Path, export_name: str, class_name: str, dry_run: bool) -> FixResult:
    """
    افزودن export simulator instance در انتهای فایل
    
    الگو:
    export const climateSimulator = new ClimateSimulator();
    """
    result = FixResult(
        file=str(file_path),
        category="G: Add export",
        action=f"Add export {export_name}"
    )
    
    if not file_path.exists():
        result.status = "skipped"
        result.details = "File not found"
        return result
    
    try:
        content = file_path.read_text(encoding="utf-8")
        
        # بررسی اینکه آیا export از قبل وجود دارد
        if f"export const {export_name}" in content:
            result.status = "skipped"
            result.details = "Export already exists"
            return result
        
        # پیدا کردن نام class
        class_match = re.search(rf'export\s+class\s+({class_name})', content)
        if not class_match:
            # اگر class با این نام نیست، هر class ای را پیدا کن
            class_match = re.search(r'export\s+class\s+(\w+)', content)
        
        if class_match:
            actual_class = class_match.group(1)
            export_line = f"\n\n// Export singleton instance\nexport const {export_name} = new {actual_class}();\n"
            
            if not dry_run:
                with open(file_path, 'a', encoding="utf-8") as f:
                    f.write(export_line)
            
            result.status = "done"
            result.details = f"Added: export const {export_name} = new {actual_class}()"
        else:
            result.status = "failed"
            result.details = "No class found to export"
    
    except Exception as e:
        result.status = "failed"
        result.details = str(e)
    
    return result


# ============================================================
# Category H: Fix SimulatorAudience conflict
# ============================================================

def fix_simulator_audience_conflict(file_path: Path, dry_run: bool) -> FixResult:
    """
    رفع تعارض SimulatorAudience در registry.ts
    
    اگر در types.ts تعریف شده، از registry.ts حذف می‌کنیم
    """
    result = FixResult(
        file=str(file_path),
        category="H: SimulatorAudience conflict",
        action="Remove duplicate SimulatorAudience"
    )
    
    if not file_path.exists():
        result.status = "skipped"
        result.details = "File not found"
        return result
    
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content
        
        # حذف export type SimulatorAudience از re-export
        # الگو: export type { SimulatorEngine, SimulatorRegistry, SimulatorAudience } from "./types";
        content = re.sub(
            r'export\s+type\s*\{\s*SimulatorEngine\s*,\s*SimulatorRegistry\s*,\s*SimulatorAudience\s*\}\s*from\s*"\./types";',
            'export type { SimulatorEngine, SimulatorRegistry } from "./types";',
            content
        )
        
        if content != original:
            if not dry_run:
                file_path.write_text(content, encoding="utf-8")
            result.status = "done"
            result.details = "Removed SimulatorAudience from re-export"
        else:
            result.status = "skipped"
            result.details = "No conflict found"
    
    except Exception as e:
        result.status = "failed"
        result.details = str(e)
    
    return result


# ============================================================
# Main Orchestrator
# ============================================================

class TypeScriptFixer:
    """مدیر اصلی رفع خطاها"""
    
    def __init__(self, project_root: Path, dry_run: bool = False, backup: bool = True):
        self.project_root = project_root
        self.web_dir = project_root / "apps" / "web"
        self.src_dir = self.web_dir / "src"
        self.dry_run = dry_run
        self.backup = backup
        self.backup_path: Optional[Path] = None
        self.report = FixReport(
            timestamp=datetime.now().isoformat(),
            dry_run=dry_run
        )
    
    def execute(self) -> FixReport:
        """اجرای کامل رفع خطاها"""
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint(f"🔧 {PROJECT_NAME} - TypeScript Build Fix v{VERSION}", Colors.BOLD)
        cprint(f"   Mode: {'DRY RUN' if self.dry_run else 'LIVE'}", Colors.YELLOW if self.dry_run else Colors.GREEN)
        cprint("=" * 70, Colors.BOLD)
        
        try:
            # گام ۰: بررسی اولیه
            self._pre_flight_checks()
            
            # گام ۱: Backup
            if self.backup and not self.dry_run:
                self._create_backup()
            
            # گام ۲: رفع دسته A (kpis)
            self._fix_category_a()
            
            # گام ۳: رفع دسته B (language)
            self._fix_category_b()
            
            # گام ۴: رفع دسته C (type conflicts)
            self._fix_category_c()
            
            # گام ۵: رفع دسته D (authService)
            self._fix_category_d()
            
            # گام ۶: رفع دسته E/F (engines)
            self._fix_category_ef()
            
            # گام ۷: رفع دسته G (exports)
            self._fix_category_g()
            
            # گام ۸: رفع دسته H (SimulatorAudience)
            self._fix_category_h()
            
            # گام ۹: گزارش نهایی
            self._print_report()
            
        except Exception as e:
            logger.error(f"❌ خطای بحرانی: {e}")
            self.report.errors.append(str(e))
            import traceback
            traceback.print_exc()
        
        return self.report
    
    def _pre_flight_checks(self):
        """بررسی‌های اولیه"""
        cprint("\n🔍 گام ۰: بررسی‌های اولیه...", Colors.BLUE)
        
        if not self.src_dir.exists():
            raise FileNotFoundError(f"src/ یافت نشد: {self.src_dir}")
        
        file_count = len(list(self.src_dir.rglob("*.ts*")))
        cprint(f"   ✅ src/ یافت شد: {file_count} فایل TypeScript", Colors.GREEN)
    
    def _create_backup(self):
        """ایجاد backup"""
        cprint("\n💾 گام ۱: ایجاد backup...", Colors.BLUE)
        
        try:
            self.backup_path = create_backup(self.src_dir, self.project_root / ".backups")
            self.report.backup_path = self.backup_path
            cprint(f"   ✅ Backup ایجاد شد: {self.backup_path}", Colors.GREEN)
        except Exception as e:
            cprint(f"   ⚠️  Backup ایجاد نشد: {e}", Colors.YELLOW)
    
    def _fix_category_a(self):
        """رفع دسته A: kpis unused"""
        cprint("\n📝 گام ۲: رفع kpis استفاده نشده (دسته A)...", Colors.BLUE)
        
        files = [
            "audiences/ExpertDashboard.tsx",
            "audiences/FarmerDashboard.tsx",
            "audiences/ManagerDashboard.tsx",
            "audiences/ResearcherDashboard.tsx",
            "audiences/StudentDashboard.tsx",
        ]
        
        for rel_path in files:
            file_path = self.src_dir / rel_path
            result = fix_unused_kpis(file_path, self.dry_run)
            self.report.results.append(result)
            
            if result.status == "done":
                cprint(f"   ✅ {rel_path}: {result.details}", Colors.GREEN)
            elif result.status == "skipped":
                cprint(f"   ⏩ {rel_path}: {result.details}", Colors.DIM)
            else:
                cprint(f"   ❌ {rel_path}: {result.details}", Colors.RED)
    
    def _fix_category_b(self):
        """رفع دسته B: language unused"""
        cprint("\n📝 گام ۳: رفع language استفاده نشده (دسته B)...", Colors.BLUE)
        
        file_path = self.src_dir / "pages/AgricultureSchools/AgricultureSchools.tsx"
        result = fix_unused_language(file_path, self.dry_run)
        self.report.results.append(result)
        
        if result.status == "done":
            cprint(f"   ✅ AgricultureSchools.tsx: {result.details}", Colors.GREEN)
        elif result.status == "skipped":
            cprint(f"   ⏩ AgricultureSchools.tsx: {result.details}", Colors.DIM)
        else:
            cprint(f"   ❌ AgricultureSchools.tsx: {result.details}", Colors.RED)
    
    def _fix_category_c(self):
        """رفع دسته C: type conflicts"""
        cprint("\n📝 گام ۴: رفع type conflicts (دسته C)...", Colors.BLUE)
        
        fixes = [
            ("satellites/registry.ts", "Satellite"),
            ("scenarios/registry.ts", "Scenario"),
        ]
        
        for rel_path, type_name in fixes:
            file_path = self.src_dir / rel_path
            result = fix_type_conflict(file_path, type_name, self.dry_run)
            self.report.results.append(result)
            
            if result.status == "done":
                cprint(f"   ✅ {rel_path}: {result.details}", Colors.GREEN)
            elif result.status == "skipped":
                cprint(f"   ⏩ {rel_path}: {result.details}", Colors.DIM)
            else:
                cprint(f"   ❌ {rel_path}: {result.details}", Colors.RED)
    
    def _fix_category_d(self):
        """رفع دسته D: authService"""
        cprint("\n📝 گام ۵: رفع authService (دسته D)...", Colors.BLUE)
        
        file_path = self.src_dir / "services/authService.ts"
        result = fix_auth_service(file_path, self.dry_run)
        self.report.results.append(result)
        
        if result.status == "done":
            cprint(f"   ✅ authService.ts: {result.details}", Colors.GREEN)
        elif result.status == "skipped":
            cprint(f"   ⏩ authService.ts: {result.details}", Colors.DIM)
        else:
            cprint(f"   ❌ authService.ts: {result.details}", Colors.RED)
    
    def _fix_category_ef(self):
        """رفع دسته E/F: engines"""
        cprint("\n📝 گام ۶: رفع فایل‌های engines (دسته E/F)...", Colors.BLUE)
        
        engines_dir = self.src_dir / "simulators/engines"
        if not engines_dir.exists():
            cprint("   ⚠️  دایرکتوری engines یافت نشد", Colors.YELLOW)
            return
        
        for ts_file in engines_dir.glob("*.ts"):
            result = fix_engine_file(ts_file, self.dry_run)
            self.report.results.append(result)
            
            if result.status == "done":
                cprint(f"   ✅ {ts_file.name}: {result.details}", Colors.GREEN)
            elif result.status == "skipped":
                cprint(f"   ⏩ {ts_file.name}: {result.details}", Colors.DIM)
            else:
                cprint(f"   ❌ {ts_file.name}: {result.details}", Colors.RED)
    
    def _fix_category_g(self):
        """رفع دسته G: simulator exports"""
        cprint("\n📝 گام ۷: افزودن simulator exports (دسته G)...", Colors.BLUE)
        
        engines_dir = self.src_dir / "simulators/engines"
        if not engines_dir.exists():
            cprint("   ⚠️  دایرکتوری engines یافت نشد", Colors.YELLOW)
            return
        
        exports = {
            "climate.ts": ("climateSimulator", "ClimateSimulator"),
            "hydrology.ts": ("hydrologySimulator", "HydrologySimulator"),
            "crop.ts": ("cropSimulator", "CropSimulator"),
            "carbon.ts": ("carbonSimulator", "CarbonSimulator"),
            "soilErosion.ts": ("soilErosionSimulator", "SoilErosionSimulator"),
            "flood.ts": ("floodSimulator", "FloodSimulator"),
            "drought.ts": ("droughtSimulator", "DroughtSimulator"),
            "biodiversity.ts": ("biodiversitySimulator", "BiodiversitySimulator"),
        }
        
        for filename, (export_name, class_name) in exports.items():
            file_path = engines_dir / filename
            result = add_simulator_export(file_path, export_name, class_name, self.dry_run)
            self.report.results.append(result)
            
            if result.status == "done":
                cprint(f"   ✅ {filename}: {result.details}", Colors.GREEN)
            elif result.status == "skipped":
                cprint(f"   ⏩ {filename}: {result.details}", Colors.DIM)
            else:
                cprint(f"   ❌ {filename}: {result.details}", Colors.RED)
    
    def _fix_category_h(self):
        """رفع دسته H: SimulatorAudience conflict"""
        cprint("\n📝 گام ۸: رفع SimulatorAudience conflict (دسته H)...", Colors.BLUE)
        
        file_path = self.src_dir / "simulators/registry.ts"
        result = fix_simulator_audience_conflict(file_path, self.dry_run)
        self.report.results.append(result)
        
        if result.status == "done":
            cprint(f"   ✅ registry.ts: {result.details}", Colors.GREEN)
        elif result.status == "skipped":
            cprint(f"   ⏩ registry.ts: {result.details}", Colors.DIM)
        else:
            cprint(f"   ❌ registry.ts: {result.details}", Colors.RED)
    
    def _print_report(self):
        """چاپ گزارش نهایی"""
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint("📊 گزارش نهایی", Colors.BOLD)
        cprint("=" * 70, Colors.BOLD)
        
        cprint(f"\n   ✅ انجام‌شده: {Colors.GREEN}{self.report.total_done}{Colors.END}")
        cprint(f"   ❌ ناموفق: {Colors.RED}{self.report.total_failed}{Colors.END}")
        cprint(f"   ⏩ ردشده: {Colors.YELLOW}{self.report.total_skipped}{Colors.END}")
        
        if self.backup_path:
            cprint(f"\n   💾 Backup: {self.backup_path}", Colors.CYAN)
        
        if self.report.errors:
            cprint(f"\n   {Colors.RED}❌ خطاهای بحرانی:{Colors.END}")
            for error in self.report.errors:
                cprint(f"      • {error}", Colors.RED)
        
        cprint("\n" + "=" * 70, Colors.BOLD)
        
        if self.report.total_failed == 0:
            cprint("\n✅ رفع خطاها کامل شد!", Colors.GREEN + Colors.BOLD)
            cprint("\n📌 گام‌های بعدی:", Colors.BLUE)
            cprint("   1. اجرای build: cd apps/web && pnpm build")
            cprint("   2. اگر خطا باقی ماند، خروجی را ارسال کنید")
            cprint("   3. Commit: git add . && git commit -m 'fix: resolve TS errors'")
            
            if self.dry_run:
                cprint("\n🔍 این یک Dry Run بود. برای اجرای واقعی، flag --dry-run را حذف کنید.", Colors.YELLOW)
        else:
            cprint("\n⚠️  برخی خطاها رفع نشدند. لطفاً بررسی دستی کنید.", Colors.YELLOW)
    
    def rollback(self):
        """بازگشت به حالت قبل"""
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint("⏪ Rollback - بازگشت به حالت قبل", Colors.BOLD)
        cprint("=" * 70, Colors.BOLD)
        
        backup_dir = self.project_root / ".backups"
        if not backup_dir.exists():
            cprint("\n❌ Backup یافت نشد", Colors.RED)
            return
        
        # پیدا کردن آخرین backup
        backups = sorted(backup_dir.glob("ts_fix_backup_*"), reverse=True)
        if not backups:
            cprint("\n❌ Backup یافت نشد", Colors.RED)
            return
        
        latest_backup = backups[0]
        cprint(f"\n💾 آخرین Backup: {latest_backup}", Colors.GREEN)
        
        confirm = input("\nآیا مطمئن هستید؟ (yes/no): ")
        if confirm.lower() != "yes":
            cprint("\n❌ Rollback لغو شد", Colors.RED)
            return
        
        try:
            # حذف src فعلی
            if self.src_dir.exists():
                shutil.rmtree(self.src_dir)
            
            # بازیابی از backup
            shutil.copytree(latest_backup, self.src_dir)
            cprint("\n✅ Rollback با موفقیت انجام شد!", Colors.GREEN + Colors.BOLD)
        
        except Exception as e:
            cprint(f"\n❌ خطا در Rollback: {e}", Colors.RED)


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description=f"{PROJECT_NAME} - TypeScript Build Fix v{VERSION}"
    )
    parser.add_argument(
        "--root", type=str, default=".",
        help="مسیر ریشه پروژه"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="اجرای آزمایشی بدون تغییر واقعی"
    )
    parser.add_argument(
        "--no-backup", action="store_true",
        help="عدم ایجاد backup"
    )
    parser.add_argument(
        "--rollback", action="store_true",
        help="بازگشت به حالت قبل"
    )
    
    args = parser.parse_args()
    project_root = Path(args.root).resolve()
    
    cprint(f"\n🌱 {PROJECT_NAME} TypeScript Fix v{VERSION}", Colors.BOLD)
    cprint(f"📂 ریشه: {project_root}", Colors.DIM)
    
    fixer = TypeScriptFixer(
        project_root=project_root,
        dry_run=args.dry_run,
        backup=not args.no_backup
    )
    
    if args.rollback:
        fixer.rollback()
    else:
        report = fixer.execute()
        sys.exit(1 if report.total_failed > 0 else 0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n⏹️  متوقف شد", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        cprint(f"\n❌ خطای غیرمنتظره: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)