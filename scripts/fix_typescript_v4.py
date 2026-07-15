#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - TypeScript Build Fix v4.0 (Simple & Direct)
========================================================
اسکریپت ساده و مستقیم برای رفع ۴۱ خطای باقی‌مانده

استراتژی:
- regex های ساده و دقیق
- replace مستقیم به جای pattern matching پیچیده
- fallback برای هر عملیات

نحوه اجرا:
    python scripts/testing/fix_typescript_v4.py
"""

import re
from pathlib import Path
from typing import Tuple

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


# ============================================================
# 1. Fix kpis unused (5 files)
# ============================================================

def fix_kpis(file_path: Path) -> Tuple[bool, str]:
    """حذف کامل بلاک kpis"""
    if not file_path.exists():
        return False, "File not found"
    
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    # پیدا کردن خط شروع kpis
    lines = content.split('\n')
    new_lines = []
    skip_until_close = False
    brace_count = 0
    
    for i, line in enumerate(lines):
        if 'const kpis = {' in line:
            # شروع حذف
            skip_until_close = True
            brace_count = line.count('{') - line.count('}')
            new_lines.append('  // TODO: kpis not used - implement or remove')
            continue
        
        if skip_until_close:
            brace_count += line.count('{') - line.count('}')
            if brace_count <= 0:
                skip_until_close = False
            continue
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True, "kpis block removed"
    return False, "No kpis found"


# ============================================================
# 2. Fix language unused (2 occurrences)
# ============================================================

def fix_language(file_path: Path) -> Tuple[bool, str]:
    """حذف language از destructuring"""
    if not file_path.exists():
        return False, "File not found"
    
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    # Replace مستقیم
    content = content.replace(
        'const { t, dir, language } = useLanguage()',
        'const { t, dir } = useLanguage()'
    )
    
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True, "language removed"
    return False, "No language found"


# ============================================================
# 3. Fix Satellite type
# ============================================================

def fix_satellite_type(file_path: Path) -> Tuple[bool, str]:
    """افزودن import Satellite"""
    if not file_path.exists():
        return False, "File not found"
    
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    # بررسی اینکه آیا Satellite از قبل import شده
    if 'import type { Satellite }' in content or 'import { Satellite }' in content:
        return False, "Already imported"
    
    # افزودن import در ابتدای فایل
    lines = content.split('\n')
    new_lines = []
    import_added = False
    
    for line in lines:
        if not import_added and line.startswith('import'):
            new_lines.append('import type { Satellite } from "./types";')
            import_added = True
        new_lines.append(line)
    
    if not import_added:
        new_lines.insert(0, 'import type { Satellite } from "./types";')
    
    content = '\n'.join(new_lines)
    
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True, "Satellite import added"
    return False, "No change"


# ============================================================
# 4. Fix Scenario type
# ============================================================

def fix_scenario_type(file_path: Path) -> Tuple[bool, str]:
    """افزودن import Scenario"""
    if not file_path.exists():
        return False, "File not found"
    
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    if 'import type { Scenario }' in content or 'import { Scenario }' in content:
        return False, "Already imported"
    
    lines = content.split('\n')
    new_lines = []
    import_added = False
    
    for line in lines:
        if not import_added and line.startswith('import'):
            new_lines.append('import type { Scenario } from "./types";')
            import_added = True
        new_lines.append(line)
    
    if not import_added:
        new_lines.insert(0, 'import type { Scenario } from "./types";')
    
    content = '\n'.join(new_lines)
    
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True, "Scenario import added"
    return False, "No change"


# ============================================================
# 5. Fix authService return type
# ============================================================

def fix_auth_service(file_path: Path) -> Tuple[bool, str]:
    """تغییر return type به MeResponse"""
    if not file_path.exists():
        return False, "File not found"
    
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    # Replace مستقیم
    content = content.replace(
        'async getMe(): Promise<User>',
        'async getMe(): Promise<MeResponse>'
    )
    
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True, "Return type changed"
    return False, "No change"


# ============================================================
# 6. Fix engines - Remove visualize method
# ============================================================

def fix_engine_visualize(file_path: Path) -> Tuple[bool, str]:
    """حذف کامل متد visualize"""
    if not file_path.exists():
        return False, "File not found"
    
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    lines = content.split('\n')
    new_lines = []
    skip_method = False
    brace_count = 0
    
    for line in lines:
        if 'visualize(' in line and 'VisualizationSpec' in line:
            skip_method = True
            brace_count = line.count('{') - line.count('}')
            continue
        
        if skip_method:
            brace_count += line.count('{') - line.count('}')
            if brace_count <= 0:
                skip_method = False
            continue
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True, "visualize method removed"
    return False, "No visualize found"


# ============================================================
# 7. Add simulator exports
# ============================================================

def add_simulator_export(file_path: Path, export_name: str) -> Tuple[bool, str]:
    """افزودن export simulator"""
    if not file_path.exists():
        return False, "File not found"
    
    content = file_path.read_text(encoding="utf-8")
    
    if f'export const {export_name}' in content:
        return False, "Already exported"
    
    # پیدا کردن class name
    class_match = re.search(r'export class (\w+)', content)
    if not class_match:
        return False, "No class found"
    
    class_name = class_match.group(1)
    export_line = f'\n\nexport const {export_name} = new {class_name}();\n'
    
    with open(file_path, 'a', encoding="utf-8") as f:
        f.write(export_line)
    
    return True, f"Added export {export_name}"


# ============================================================
# Main
# ============================================================

def main():
    cprint("\n" + "=" * 70, Colors.BOLD)
    cprint("🔧 TypeScript Build Fix v4.0 - Simple & Direct", Colors.BOLD)
    cprint("=" * 70, Colors.BOLD)
    
    fixed_count = 0
    
    # 1. Fix kpis
    cprint("\n📝 Fixing kpis unused...", Colors.BLUE)
    kpis_files = [
        "audiences/ExpertDashboard.tsx",
        "audiences/FarmerDashboard.tsx",
        "audiences/ManagerDashboard.tsx",
        "audiences/ResearcherDashboard.tsx",
        "audiences/StudentDashboard.tsx",
    ]
    
    for rel_path in kpis_files:
        file_path = WEB_DIR / rel_path
        ok, msg = fix_kpis(file_path)
        if ok:
            cprint(f"   ✅ {rel_path}: {msg}", Colors.GREEN)
            fixed_count += 1
        else:
            cprint(f"   ⏩ {rel_path}: {msg}", Colors.YELLOW)
    
    # 2. Fix language
    cprint("\n📝 Fixing language unused...", Colors.BLUE)
    file_path = WEB_DIR / "pages/AgricultureSchools/AgricultureSchools.tsx"
    ok, msg = fix_language(file_path)
    if ok:
        cprint(f"   ✅ AgricultureSchools.tsx: {msg}", Colors.GREEN)
        fixed_count += 1
    else:
        cprint(f"   ⏩ AgricultureSchools.tsx: {msg}", Colors.YELLOW)
    
    # 3. Fix Satellite type
    cprint("\n📝 Fixing Satellite type...", Colors.BLUE)
    file_path = WEB_DIR / "satellites/registry.ts"
    ok, msg = fix_satellite_type(file_path)
    if ok:
        cprint(f"   ✅ satellites/registry.ts: {msg}", Colors.GREEN)
        fixed_count += 1
    else:
        cprint(f"   ⏩ satellites/registry.ts: {msg}", Colors.YELLOW)
    
    # 4. Fix Scenario type
    cprint("\n📝 Fixing Scenario type...", Colors.BLUE)
    file_path = WEB_DIR / "scenarios/registry.ts"
    ok, msg = fix_scenario_type(file_path)
    if ok:
        cprint(f"   ✅ scenarios/registry.ts: {msg}", Colors.GREEN)
        fixed_count += 1
    else:
        cprint(f"   ⏩ scenarios/registry.ts: {msg}", Colors.YELLOW)
    
    # 5. Fix authService
    cprint("\n📝 Fixing authService...", Colors.BLUE)
    file_path = WEB_DIR / "services/authService.ts"
    ok, msg = fix_auth_service(file_path)
    if ok:
        cprint(f"   ✅ authService.ts: {msg}", Colors.GREEN)
        fixed_count += 1
    else:
        cprint(f"   ⏩ authService.ts: {msg}", Colors.YELLOW)
    
    # 6. Fix engines
    cprint("\n📝 Fixing engines...", Colors.BLUE)
    engines_dir = WEB_DIR / "simulators/engines"
    if engines_dir.exists():
        for ts_file in engines_dir.glob("*.ts"):
            ok, msg = fix_engine_visualize(ts_file)
            if ok:
                cprint(f"   ✅ {ts_file.name}: {msg}", Colors.GREEN)
                fixed_count += 1
            else:
                cprint(f"   ⏩ {ts_file.name}: {msg}", Colors.YELLOW)
    
    # 7. Add simulator exports
    cprint("\n📝 Adding simulator exports...", Colors.BLUE)
    exports = {
        "climate.ts": "climateSimulator",
        "hydrology.ts": "hydrologySimulator",
        "crop.ts": "cropSimulator",
        "carbon.ts": "carbonSimulator",
        "soilErosion.ts": "soilErosionSimulator",
        "flood.ts": "floodSimulator",
        "drought.ts": "droughtSimulator",
        "biodiversity.ts": "biodiversitySimulator",
    }
    
    for filename, export_name in exports.items():
        file_path = engines_dir / filename
        ok, msg = add_simulator_export(file_path, export_name)
        if ok:
            cprint(f"   ✅ {filename}: {msg}", Colors.GREEN)
            fixed_count += 1
        else:
            cprint(f"   ⏩ {filename}: {msg}", Colors.YELLOW)
    
    # Summary
    cprint("\n" + "=" * 70, Colors.BOLD)
    cprint(f"✅ {fixed_count} fixes applied", Colors.BOLD)
    cprint("=" * 70, Colors.BOLD)
    
    cprint("\n📌 Next steps:", Colors.BLUE)
    cprint("   1. Run: cd apps/web && pnpm build")
    cprint("   2. If errors remain, send output")
    cprint("   3. Commit: git add . && git commit -m 'fix: resolve TS errors'")


if __name__ == "__main__":
    main()