#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - TypeScript Build Fix (Automated)
=============================================
رفع خودکار خطاهای گروه A (unused) و B (exports)

نحوه اجرا:
    python scripts/testing/fix_typescript_errors.py
"""

import re
import sys
from pathlib import Path
from typing import Tuple
from dataclasses import dataclass, field

@dataclass
class FixResult:
    file: str
    fixes: list = field(default_factory=list)
    status: str = "pending"

WEB_DIR = Path("apps/web/src")

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def cprint(msg: str, color: str = Colors.END):
    print(f"{color}{msg}{Colors.END}")


def fix_unused_language(file_path: Path) -> Tuple[bool, str]:
    """حذف language از destructuring useLanguage"""
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    # الگو: const { t, dir, language } = useLanguage();
    # تبدیل: const { t, dir } = useLanguage();
    content = re.sub(
        r"const\s*\{\s*t\s*,\s*dir\s*,\s*language\s*\}\s*=\s*useLanguage\(\)",
        "const { t, dir } = useLanguage()",
        content
    )
    
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True, "language removed"
    return False, ""


def fix_unused_kpis(file_path: Path) -> Tuple[bool, str]:
    """تبدیل kpis unused به _kpis (underscore = intentionally unused)"""
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    # اگر kpis تعریف شده اما استفاده نشده، آن را کامنت می‌کنیم
    # روش امن: اضافه کردن // eslint-disable-next-line @typescript-eslint/no-unused-vars
    lines = content.split("\n")
    new_lines = []
    in_kpis_block = False
    kpis_start_idx = -1
    
    for i, line in enumerate(lines):
        if re.match(r"\s*const\s+kpis\s*=\s*\{", line):
            # بررسی اینکه آیا kpis استفاده شده
            rest = "\n".join(lines[i:])
            # شمارش استفاده‌های kpis (بعد از تعریف)
            usage_count = len(re.findall(r"\bkpis\b", rest)) - 1
            if usage_count == 0:
                # اضافه کردن کامنت در ابتدای بلاک
                new_lines.append("  // eslint-disable-next-line @typescript-eslint/no-unused-vars")
                kpis_start_idx = i
                in_kpis_block = True
        
        new_lines.append(line)
    
    if kpis_start_idx >= 0:
        content = "\n".join(new_lines)
        file_path.write_text(content, encoding="utf-8")
        return True, "kpis marked as intentionally unused"
    return False, ""


def fix_unused_imports(file_path: Path) -> Tuple[bool, str]:
    """حذف imports استفاده نشده (Link, cn)"""
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    fixes = []
    
    # بررسی Link
    if 'import { Link } from "react-router-dom"' in content:
        if content.count("Link") == 1:  # فقط import
            content = content.replace('import { Link } from "react-router-dom";\n', '')
            fixes.append("Link")
    
    # بررسی cn
    if 'import { cn } from "@/lib/utils"' in content:
        if content.count("cn") == 1:
            content = content.replace('import { cn } from "@/lib/utils";\n', '')
            fixes.append("cn")
    
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True, f"removed: {', '.join(fixes)}"
    return False, ""


def fix_simulator_visualize(file_path: Path) -> Tuple[bool, str]:
    """اصلاح متد visualize که result استفاده نمی‌شود"""
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    # الگو: visualize(result): VisualizationSpec {
    # تبدیل: visualize(_result): VisualizationSpec {
    # یا بهتر: با prefix underscore
    content = re.sub(
        r"visualize\(result\)\s*:\s*VisualizationSpec",
        "visualize(_result): VisualizationSpec",
        content
    )
    
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True, "result -> _result"
    return False, ""


def fix_simulator_exports(file_path: Path, simulator_name: str) -> Tuple[bool, str]:
    """افزودن export برای simulator های گم‌شده"""
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    # اگر export climateSimulator وجود ندارد، اضافه کن
    if f"export const {simulator_name}" not in content and \
       f"export {simulator_name}" not in content:
        
        # پیدا کردن class Simulator و export کردن یک instance
        class_match = re.search(r"export\s+class\s+(\w+Simulator|Simulator)", content)
        if class_match:
            class_name = class_match.group(1)
            # اضافه کردن export در انتها
            content = content.rstrip() + f"\n\nexport const {simulator_name} = new {class_name}();\n"
            
            file_path.write_text(content, encoding="utf-8")
            return True, f"added: export const {simulator_name}"
    
    return False, ""


def fix_time_series_chart(file_path: Path) -> Tuple[bool, str]:
    """اصلاح TimeSeriesChart.tsx"""
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    # حذف arr از destructuring
    content = content.replace(
        ".map((d, i, arr) => {",
        ".map((d, i) => {"
    )
    
    # کامنت کردن originalIdx unused
    content = re.sub(
        r"(\s*)const originalIdx = data\.indexOf\(d\);",
        r"\1// const originalIdx = data.indexOf(d); // unused",
        content
    )
    
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True, "arr and originalIdx fixed"
    return False, ""


def main():
    cprint("\n" + "=" * 70, Colors.BOLD)
    cprint("🔧 TypeScript Build Fix - Automated", Colors.BOLD)
    cprint("=" * 70, Colors.BOLD)
    
    results = []
    
    # گروه A: رفع unused variables
    cprint("\n📝 گروه A: رفع متغیرهای استفاده نشده...", Colors.BLUE)
    
    audience_files = [
        "audiences/ExpertDashboard.tsx",
        "audiences/FarmerDashboard.tsx",
        "audiences/ManagerDashboard.tsx",
        "audiences/ResearcherDashboard.tsx",
        "audiences/StudentDashboard.tsx",
    ]
    
    for rel_path in audience_files:
        file_path = WEB_DIR / rel_path
        if not file_path.exists():
            continue
        
        r = FixResult(file=rel_path)
        
        ok, msg = fix_unused_language(file_path)
        if ok: r.fixes.append(msg)
        
        ok, msg = fix_unused_kpis(file_path)
        if ok: r.fixes.append(msg)
        
        ok, msg = fix_unused_imports(file_path)
        if ok: r.fixes.append(msg)
        
        if r.fixes:
            r.status = "done"
            cprint(f"   ✅ {rel_path}: {', '.join(r.fixes)}", Colors.GREEN)
        else:
            r.status = "skipped"
        
        results.append(r)
    
    # گروه A (ادامه): سایر فایل‌ها
    other_files = [
        ("pages/AgricultureSchools/AgricultureSchools.tsx", ["language", "cn"]),
        ("pages/ContactUs/ContactUs.tsx", ["cn"]),
        ("components/charts/TimeSeriesChart.tsx", ["arr"]),
        ("simulators/components/SimulatorRunner.tsx", ["cn"]),
        ("simulators/pages/SimulatorsIndexPage.tsx", ["cn"]),
    ]
    
    for rel_path, issues in other_files:
        file_path = WEB_DIR / rel_path
        if not file_path.exists():
            continue
        
        r = FixResult(file=rel_path)
        
        if "language" in issues:
            ok, msg = fix_unused_language(file_path)
            if ok: r.fixes.append(msg)
        
        ok, msg = fix_unused_imports(file_path)
        if ok: r.fixes.append(msg)
        
        if rel_path == "components/charts/TimeSeriesChart.tsx":
            ok, msg = fix_time_series_chart(file_path)
            if ok: r.fixes.append(msg)
        
        if r.fixes:
            r.status = "done"
            cprint(f"   ✅ {rel_path}: {', '.join(r.fixes)}", Colors.GREEN)
        
        results.append(r)
    
    # گروه A: اصلاح visualize methods
    cprint("\n📝 گروه A: اصلاح visualize methods...", Colors.BLUE)
    
    engines_dir = WEB_DIR / "simulators/engines"
    if engines_dir.exists():
        for ts_file in engines_dir.glob("*.ts"):
            ok, msg = fix_simulator_visualize(ts_file)
            if ok:
                cprint(f"   ✅ {ts_file.name}: {msg}", Colors.GREEN)
                results.append(FixResult(file=str(ts_file), fixes=[msg], status="done"))
    
    # گروه B: افزودن exports
    cprint("\n📝 گروه B: افزودن exports گم‌شده...", Colors.BLUE)
    
    simulator_exports = {
        "climate.ts": "climateSimulator",
        "hydrology.ts": "hydrologySimulator",
        "crop.ts": "cropSimulator",
        "carbon.ts": "carbonSimulator",
        "soilErosion.ts": "soilErosionSimulator",
        "flood.ts": "floodSimulator",
        "drought.ts": "droughtSimulator",
        "biodiversity.ts": "biodiversitySimulator",
    }
    
    for filename, export_name in simulator_exports.items():
        file_path = engines_dir / filename
        if file_path.exists():
            ok, msg = fix_simulator_exports(file_path, export_name)
            if ok:
                cprint(f"   ✅ {filename}: {msg}", Colors.GREEN)
                results.append(FixResult(file=filename, fixes=[msg], status="done"))
    
    # خلاصه
    cprint("\n" + "=" * 70, Colors.BOLD)
    done_count = sum(1 for r in results if r.status == "done")
    cprint(f"✅ {done_count} فایل اصلاح شد", Colors.BOLD)
    cprint("=" * 70, Colors.BOLD)
    
    cprint("\n📌 گام بعدی:", Colors.BLUE)
    cprint("   1. اجرای build: cd apps/web && pnpm build")
    cprint("   2. رفع خطاهای باقی‌مانده (گروه C و D) به صورت دستی")
    cprint("   3. Commit: git add . && git commit -m 'fix: resolve typescript build errors'")


if __name__ == "__main__":
    main()