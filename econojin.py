#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
  🚀 Econojin Master v3.1 - اسکریپت واحد
  سازنده: Super Z (Z.ai)
============================================================

فازها:
  phase0   - پاکسازی پروژه
  phase1   - تحلیل refactor + تولید template
  phase2   - اجرای واقعی refactor فایل‌ها
  status   - وضعیت پروژه
  all      - همه فازها

مثال:
  python econojin.py status
  python econojin.py phase0 --execute
  python econojin.py phase2 --file ProductionGIS
"""

import os
import sys
import re
import json
import shutil
import argparse
import platform
import subprocess
from pathlib import Path
from datetime import datetime


class C:
    RESET = "\033[0m"; BOLD = "\033[1m"; RED = "\033[91m"; GREEN = "\033[92m"
    YELLOW = "\033[93m"; BLUE = "\033[94m"; MAGENTA = "\033[95m"; CYAN = "\033[96m"; GRAY = "\033[90m"

    @staticmethod
    def enable_windows():
        if platform.system() == "Windows":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except: pass


PROJECT_PATH = Path(r"D:\econojin.com")

JUNK_FILES = {
    'files.txt', 'report.json', 'orphans_list.txt', 'dependency_graph.dot',
    'MERGE_PLAN.json', 'project_analyzer', 'react-18.2.0.tgz',
    'restore_from_backup.ps1', 'fix_venv.ps1',
    # اسکریپت‌های اضافی که باید حذف شن
    'cleanup.py', 'cleanup_v2.py', 'verify_cleanup.py',
    'project_analyzer.py', 'refactor_analyzer.py',
    'refactor_production_gis.py', 'apps_analyzer_v1.1.py',
    'apps_analyzer_v1.2.py', 'dependency_analyzer.py',
    'deep_secret_scanner.py',
}

BACKUP_DIRS = {
    '.cleanup_backup', '.migration_backup', '.structure_backup',
    'apps_backup_20260711_025121', '_COLD_STORAGE',
}

CACHE_DIRS = {'.pnpm-store', '.venv-1', '.venv-2', 'venv-1', 'venv-2'}

ROOT_SCRIPTS = {
    'eco.py', 'migration_script.py', 'discover.py', 'run_econojin.py',
    'analyze_project.py', 'install_venv.ps1', 'install_packages.sh',
    'create_structure.py', 'merge_api_structure.py', 'fix_project.py',
    'inspect_api_router.py',
}

SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', '.next', '.nuxt', 'dist',
    'build', '.cache', '.pytest_cache', '.mypy_cache', '.venv',
    '.gradle', 'target', 'bin', 'obj', 'analysis_reports', 'scripts',
    '.pnpm-store', '.venv-1', '.venv-2',
}

CODE_EXTENSIONS = {'.tsx', '.ts', '.py'}


class EconojinMaster:
    def __init__(self):
        self.path = PROJECT_PATH

    def _h(self, size):
        for u in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024: return f"{size:.2f} {u}"
            size /= 1024
        return f"{size:.2f} PB"

    def _dir_size(self, d):
        total = 0
        try:
            for root, dirs, files in os.walk(d):
                for f in files:
                    try: total += (Path(root) / f).stat().st_size
                    except: pass
        except: pass
        return total

    def _print_header(self, title):
        print(f"\n{C.MAGENTA}{C.BOLD}╔{'═'*58}╗{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}║  {title:<56}║{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}║  مسیر: {str(self.path):<51}║{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}╚{'═'*58}╝{C.RESET}")

    def _run_cmd(self, cmd):
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.path)
            return r.returncode, r.stdout, r.stderr
        except Exception as e:
            return -1, "", str(e)

    # ============================================================
    #  فاز ۰: پاکسازی
    # ============================================================
    def phase0(self, execute=False):
        self._print_header("🧹 فاز ۰: پاکسازی پروژه")
        reclaimed = 0; deleted = 0; moved = 0

        print(f"\n{C.CYAN}{C.BOLD}━━━ ۱. فایل‌های غیرضروری ━━━{C.RESET}")
        for name in JUNK_FILES:
            f = self.path / name
            if f.exists() and f.is_file():
                size = f.stat().st_size
                reclaimed += size
                print(f"  {C.RED}✗{C.RESET} {self._h(size):>10}  {name}")
                if execute:
                    try: f.unlink(); deleted += 1
                    except Exception as e: print(f"    {C.RED}خطا:{C.RESET} {e}")

        print(f"\n{C.CYAN}{C.BOLD}━━━ ۲. اسکریپت‌های ریشه ━━━{C.RESET}")
        scripts_dir = self.path / 'scripts'
        if execute: scripts_dir.mkdir(exist_ok=True)
        for name in ROOT_SCRIPTS:
            f = self.path / name
            if f.exists() and f.is_file():
                print(f"  {C.BLUE}→{C.RESET} {name}")
                if execute:
                    try:
                        dst = scripts_dir / name
                        if dst.exists(): dst.unlink()
                        shutil.move(str(f), str(dst)); moved += 1
                    except Exception as e: print(f"    {C.RED}خطا:{C.RESET} {e}")

        print(f"\n{C.CYAN}{C.BOLD}━━━ ۳. پوشه‌های پشتیبان ━━━{C.RESET}")
        for name in BACKUP_DIRS:
            d = self.path / name
            if d.exists() and d.is_dir():
                size = self._dir_size(d); reclaimed += size
                print(f"  {C.RED}✗{C.RESET} {self._h(size):>10}  {name}/")
                if execute:
                    try: shutil.rmtree(d); deleted += 1
                    except Exception as e: print(f"    {C.RED}خطا:{C.RESET} {e}")

        print(f"\n{C.CYAN}{C.BOLD}━━━ ۴. پوشه‌های cache ━━━{C.RESET}")
        print(f"  {C.GRAY}(.venv فعال محافظت می‌شود){C.RESET}")
        for name in CACHE_DIRS:
            d = self.path / name
            if d.exists() and d.is_dir():
                size = self._dir_size(d); reclaimed += size
                print(f"  {C.RED}✗{C.RESET} {self._h(size):>10}  {name}/")
                if execute:
                    try: shutil.rmtree(d); deleted += 1
                    except Exception as e:
                        print(f"    {C.RED}خطا (locked):{C.RESET} {e}")
                        print(f"    {C.GRAY}پاورشل/ادیتور رو ببند{C.RESET}")

        print(f"\n{C.CYAN}{C.BOLD}━━━ ۵. __pycache__ و .pyc ━━━{C.RESET}")
        pyc_count = 0
        for root, dirs, files in os.walk(self.path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            if '__pycache__' in dirs:
                pyc_count += 1
                if execute:
                    try: shutil.rmtree(Path(root) / '__pycache__')
                    except: pass
            for f in files:
                if f.endswith('.pyc'):
                    pyc_count += 1
                    if execute:
                        try: (Path(root) / f).unlink()
                        except: pass
        print(f"  {C.YELLOW}{pyc_count} مورد{C.RESET}")
        if execute and pyc_count: print(f"  {C.GREEN}✓ حذف شد{C.RESET}")

        print(f"\n{C.CYAN}{C.BOLD}━━━ ۶. .gitignore ━━━{C.RESET}")
        gi = self.path / '.gitignore'
        if gi.exists():
            content = gi.read_text(encoding='utf-8', errors='ignore')
            missing = [p for p in ['*.db', '*.sqlite', '__pycache__', '.venv/', '.pnpm-store'] if p not in content]
            if missing:
                print(f"  {C.YELLOW}{len(missing)} الگو ناقص{C.RESET}")
                if execute:
                    with open(gi, 'a', encoding='utf-8') as f:
                        f.write("\n# Added by econojin.py\n")
                        for m in missing: f.write(f"{m}\n")
                    print(f"  {C.GREEN}✓ اضافه شد{C.RESET}")
            else: print(f"  {C.GREEN}✓ کامل است{C.RESET}")

        print(f"\n{C.MAGENTA}{C.BOLD}{'━'*50}{C.RESET}")
        print(f"  {C.CYAN}فضای قابل بازیابی:{C.RESET} {C.GREEN}{C.BOLD}{self._h(reclaimed)}{C.RESET}")
        if execute:
            print(f"  {C.GREEN}✓ حذف شده:{C.RESET} {deleted}")
            print(f"  {C.GREEN}✓ منتقل شده:{C.RESET} {moved}")
        else:
            print(f"  {C.GRAY}(پیش‌نمایش - برای اجرا --execute){C.RESET}")

        return True

    # ============================================================
    #  فاز ۱: تحلیل
    # ============================================================
    def phase1(self, execute=False, threshold=150):
        self._print_header("🔧 فاز ۱: تحلیل Refactor")
        print(f"  {C.GRAY}آستانه: {threshold} خط{C.RESET}\n")

        large_files = self._find_large_files(threshold)
        print(f"  {C.YELLOW}{len(large_files)} فایل بزرگ{C.RESET}\n")

        templates = 0
        for fp, lines in large_files:
            priority = "🔴" if lines >= 500 else ("🟠" if lines >= 250 else "🟡")
            rel = fp.relative_to(self.path)
            print(f"{C.CYAN}{priority} {C.BOLD}{lines:>5}{C.RESET} خط  {C.GRAY}{rel}{C.RESET}")
            if execute and fp.suffix == '.tsx':
                templates += self._generate_template(fp)

        print(f"\n{C.MAGENTA}{C.BOLD}{'━'*50}{C.RESET}")
        print(f"  {C.CYAN}فایل‌های بزرگ:{C.RESET} {len(large_files)}")
        print(f"  {C.RED}🔴 بحرانی:{C.RESET} {sum(1 for _,l in large_files if l>=500)}")
        print(f"  {C.RED}🟠 بالا:{C.RESET} {sum(1 for _,l in large_files if 250<=l<500)}")
        print(f"  {C.YELLOW}🟡 متوسط:{C.RESET} {sum(1 for _,l in large_files if threshold<=l<250)}")
        if execute: print(f"  {C.GREEN}✓ template‌ها:{C.RESET} {templates}")
        return True

    def _find_large_files(self, threshold):
        large = []
        for root, dirs, files in os.walk(self.path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in files:
                fp = Path(root) / f
                if fp.suffix.lower() in CODE_EXTENSIONS:
                    try:
                        with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                            lines = sum(1 for _ in fh)
                        if lines >= threshold: large.append((fp, lines))
                    except: pass
        large.sort(key=lambda x: x[1], reverse=True)
        return large

    def _generate_template(self, file_path):
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            name = file_path.stem
            if not name[0].isupper(): return 0
            count = 0
            hooks_dir = file_path.parent / 'hooks'
            utils_dir = file_path.parent / 'utils'

            has_state = bool(re.search(r'useState\s*[(<]', content))
            has_handlers = len(re.findall(r'const\s+handle\w+', content)) >= 3
            has_logic = len(re.findall(r'const\s+(calculate|format|validate)\w+', content)) >= 2

            if has_state:
                hooks_dir.mkdir(exist_ok=True)
                tmpl = hooks_dir / f'use{name}.ts'
                if not tmpl.exists():
                    tmpl.write_text(self._state_tmpl(name), encoding='utf-8')
                    count += 1; print(f"    {C.GREEN}✓{C.RESET} {tmpl.relative_to(self.path)}")
            if has_handlers:
                hooks_dir.mkdir(exist_ok=True)
                tmpl = hooks_dir / f'use{name}Handlers.ts'
                if not tmpl.exists():
                    tmpl.write_text(self._handlers_tmpl(name), encoding='utf-8')
                    count += 1; print(f"    {C.GREEN}✓{C.RESET} {tmpl.relative_to(self.path)}")
            if has_logic:
                utils_dir.mkdir(exist_ok=True)
                tmpl = utils_dir / f'{name[0].lower()+name[1:]}.ts'
                if not tmpl.exists():
                    tmpl.write_text(self._utils_tmpl(name), encoding='utf-8')
                    count += 1; print(f"    {C.GREEN}✓{C.RESET} {tmpl.relative_to(self.path)}")
            return count
        except: return 0

    def _state_tmpl(self, name):
        return f"""import {{ useState }} from 'react'

export function use{name}() {{
  // TODO: انتقال state ها از {name}
  const [loading, setLoading] = useState(false)
  return {{ loading, setLoading }}
}}
"""

    def _handlers_tmpl(self, name):
        return f"""import {{ useCallback }} from 'react'

export function use{name}Handlers() {{
  // TODO: انتقال handlers از {name}
  const handleClick = useCallback(() => {{}}, [])
  return {{ handleClick }}
}}
"""

    def _utils_tmpl(self, name):
        camel = name[0].lower() + name[1:]
        return f"""// Utils for {name}

export function format{name}Data(data: unknown) {{
  // TODO
  return data
}}
"""

    # ============================================================
    #  فاز ۲: اجرای واقعی refactor
    # ============================================================
    def phase2(self, target_file=None, execute=False):
        self._print_header("🔄 فاز ۲: اجرای Refactor")

        if not target_file:
            print(f"\n{C.YELLOW}فایل‌های آماده برای refactor:{C.RESET}")
            candidates = [
                'packages/features/src/gis/gis/ProductionGIS.tsx',
                'packages/features/src/gis/gis/SpectralIndices.tsx',
                'packages/features/src/gis/gis/AdvancedGISMap.tsx',
                'packages/features/src/gis/gis/InteractiveMap.tsx',
                'packages/features/src/gis/gis/panels/ManualLocationInput.tsx',
                'apps/web/src/pages/Chat.tsx',
                'packages/features/src/analysis/AnalysisForm.tsx',
            ]
            for i, c in enumerate(candidates, 1):
                fp = self.path / c
                if fp.exists():
                    lines = sum(1 for _ in open(fp, 'r', encoding='utf-8', errors='ignore'))
                    print(f"  {C.GREEN}{i}.{C.RESET} {lines:>5} خط  {c}")
            print(f"\n{C.CYAN}نحوه اجرا:{C.RESET}")
            print(f"  python econojin.py phase2 --file ProductionGIS")
            print(f"  python econojin.py phase2 --file ProductionGIS --execute")
            return True

        # پیدا کردن فایل
        search_patterns = [
            f'**/{target_file}.tsx',
            f'**/{target_file}.ts',
        ]
        file_path = None
        for pattern in search_patterns:
            matches = list(self.path.glob(pattern))
            matches = [m for m in matches if not any(s in str(m) for s in SKIP_DIRS)]
            if matches:
                file_path = matches[0]
                break

        if not file_path:
            print(f"\n{C.RED}❌ فایل پیدا نشد: {target_file}{C.RESET}")
            return False

        print(f"\n{C.CYAN}فایل:{C.RESET} {file_path.relative_to(self.path)}")
        print(f"{C.CYAN}حالت:{C.RESET} {'اجرای واقعی' if execute else 'پیش‌نمایش'}\n")

        if execute:
            # backup
            backup = file_path.with_suffix('.tsx.backup')
            shutil.copy2(file_path, backup)
            print(f"  {C.GREEN}✓ backup:{C.RESET} {backup.name}")

        # تحلیل
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        name = file_path.stem

        print(f"\n{C.YELLOW}{C.BOLD}━━━ تحلیل ━━━{C.RESET}")
        print(f"  {C.CYAN}کل خطوط:{C.RESET} {len(lines)}")

        # state ها
        states = []
        for i, line in enumerate(lines, 1):
            m = re.search(r'const\s+\[(\w+),\s*set(\w+)\]\s*=\s*useState', line)
            if m: states.append((i, m.group(1), m.group(2)))
        print(f"  {C.CYAN}State ها:{C.RESET} {len(states)}")
        for s in states[:5]: print(f"    • {s[1]}, set{s[2]}")
        if len(states) > 5: print(f"    {C.GRAY}... و {len(states)-5} مورد{C.RESET}")

        # handlers
        handlers = []
        for i, line in enumerate(lines, 1):
            m = re.search(r'const\s+(handle\w+)\s*=', line)
            if m: handlers.append((i, m.group(1)))
        print(f"  {C.CYAN}Handlers:{C.RESET} {len(handlers)}")
        for h in handlers[:5]: print(f"    • {h[1]}")
        if len(handlers) > 5: print(f"    {C.GRAY}... و {len(handlers)-5} مورد{C.RESET}")

        # effects
        effects = sum(1 for l in lines if 'useEffect(' in l)
        print(f"  {C.CYAN}Effects:{C.RESET} {effects}")

        # logic
        logic = []
        for i, line in enumerate(lines, 1):
            m = re.search(r'const\s+(calculate\w+|format\w+|validate\w+)\s*=', line)
            if m: logic.append((i, m.group(1)))
        print(f"  {C.CYAN}Business Logic:{C.RESET} {len(logic)}")

        # تولید فایل‌های refactor شده
        if execute:
            hooks_dir = file_path.parent / 'hooks'
            utils_dir = file_path.parent / 'utils'
            hooks_dir.mkdir(exist_ok=True)
            utils_dir.mkdir(exist_ok=True)

            # ۱. فایل state hook
            state_hook = hooks_dir / f'use{name}.ts'
            state_content = self._build_state_hook(name, states)
            state_hook.write_text(state_content, encoding='utf-8')
            print(f"\n  {C.GREEN}✓ ساخته شد:{C.RESET} {state_hook.relative_to(self.path)}")

            # ۲. فایل handlers hook
            handlers_hook = hooks_dir / f'use{name}Handlers.ts'
            handlers_content = self._build_handlers_hook(name, handlers)
            handlers_hook.write_text(handlers_content, encoding='utf-8')
            print(f"  {C.GREEN}✓ ساخته شد:{C.RESET} {handlers_hook.relative_to(self.path)}")

            # ۳. فایل utils
            if logic:
                utils_file = utils_dir / f'{name[0].lower()+name[1:]}.ts'
                utils_content = self._build_utils(name, logic)
                utils_file.write_text(utils_content, encoding='utf-8')
                print(f"  {C.GREEN}✓ ساخته شد:{C.RESET} {utils_file.relative_to(self.path)}")

            print(f"\n{C.YELLOW}⚠ توجه:{C.RESET}")
            print(f"  فایل اصلی دست‌نخورده است. حالا باید:")
            print(f"  ۱. فایل اصلی رو باز کنی")
            print(f"  ۲. state ها و handlers رو با import جایگزین کنی")
            print(f"  ۳. این دستور رو اجرا کنی: npm run build")
            print(f"  ۴. اگه کار کرد: git add . && git commit -m \"refactor: {name}\"")

        # گزارش
        report_path = self.path / 'analysis_reports'
        report_path.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report = {
            "file": str(file_path),
            "lines": len(lines),
            "states": [{"line": s[0], "name": s[1]} for s in states],
            "handlers": [{"line": h[0], "name": h[1]} for h in handlers],
            "effects": effects,
            "logic": [{"line": l[0], "name": l[1]} for l in logic],
            "executed": execute,
            "timestamp": datetime.now().isoformat(),
        }
        report_file = report_path / f"refactor_{name}_{ts}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n  {C.GRAY}گزارش:{C.RESET} {report_file.name}")

        return True

    def _build_state_hook(self, name, states):
        """ساخت فایل state hook با محتوای واقعی."""
        result = f"""import {{ useState, useEffect }} from 'react'

interface {name}State {{
"""
        for _, s, _ in states:
            result += f"  {s}: any\n"
        result += f"""}}

export function use{name}() {{
"""
        for _, s, setter in states:
            result += f"  const [{s}, set{setter}] = useState<any>(null)\n"
        result += f"""
  // TODO: منتقل کردن useEffect ها از {name}

  return {{
"""
        for _, s, _ in states:
            result += f"    {s},\n"
            result += f"    set{s[0].upper()+s[1:]},\n"
        result += f"""  }}
}}
"""
        return result

    def _build_handlers_hook(self, name, handlers):
        """ساخت فایل handlers hook."""
        result = f"""import {{ useCallback }} from 'react'

export function use{name}Handlers() {{
"""
        for _, h in handlers:
            result += f"""  const {h} = useCallback(() => {{
    // TODO: منتقل کردن logic از {h}
  }}, [])

"""
        result += f"""  return {{
"""
        for _, h in handlers:
            result += f"    {h},\n"
        result += f"""  }}
}}
"""
        return result

    def _build_utils(self, name, logic):
        """ساخت فایل utils."""
        camel = name[0].lower() + name[1:]
        result = f"// Utility functions extracted from {name}\n\n"
        for _, l in logic:
            result += f"""export function {l}(input: any) {{
  // TODO: منتقل کردن logic از {l}
  return input
}}

"""
        return result

    # ============================================================
    #  فاز ۳: رفع خطاهای build
    # ============================================================
    def phase3(self, execute=False, fix=False, show_file=None, revert=False):
        # revert: برگرداندن آخرین تغییرات fix
        if revert:
            return self._revert_fixes()

        # show: نمایش کامل یک فایل
        if show_file:
            return self._show_file_content(show_file)

        self._print_header("🔧 فاز ۳: رفع خطاهای Build")

        print(f"\n{C.CYAN}🔍 اجرای build برای پیدا کردن خطاها...{C.RESET}")

        try:
            r = subprocess.run(
                "pnpm run build",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(self.path),
            )
            output = r.stdout or ""
            returncode = r.returncode
        except Exception as e:
            print(f"  {C.RED}خطا در اجرای build:{C.RESET} {e}")
            return False

        print(f"  {C.GRAY}کد خروجی: {returncode}{C.RESET}")

        errors = []
        for line in output.split('\n'):
            m = re.search(r'([^\s]+\.tsx?)\((\d+),(\d+)\):\s*error\s*(TS\d+):\s*(.+)', line)
            if m:
                errors.append({
                    "file": m.group(1),
                    "line": int(m.group(2)),
                    "col": int(m.group(3)),
                    "code": m.group(4),
                    "message": m.group(5),
                })

        if not errors:
            if returncode != 0:
                print(f"\n  {C.YELLOW}⚠ Build شکست خورد ولی خطای TS پیدا نشد.{C.RESET}")
                print(f"  {C.GRAY}آخرین خطوط:{C.RESET}\n")
                for line in output.split('\n')[-20:]:
                    if line.strip():
                        print(f"    {C.GRAY}{line}{C.RESET}")
            else:
                print(f"\n  {C.GREEN}✓ Build موفق بود!{C.RESET}")
            return True

        print(f"\n  {C.RED}{len(errors)} خطا پیدا شد:{C.RESET}\n")

        by_file = {}
        for e in errors:
            by_file.setdefault(e["file"], []).append(e)

        for file, file_errors in by_file.items():
            print(f"  {C.YELLOW}{C.BOLD}{file}{C.RESET} ({len(file_errors)} خطا)")
            for e in file_errors[:5]:
                print(f"    {C.RED}خط {e['line']}:{e['col']}{C.RESET} {C.GRAY}[{e['code']}]{C.RESET} {e['message'][:70]}")
            if len(file_errors) > 5:
                print(f"    {C.GRAY}... و {len(file_errors)-5} خطای دیگر{C.RESET}")

        # نمایش محتوای خط‌های خطادار
        print(f"\n{C.CYAN}{C.BOLD}━━━ محتوای خط‌های خطادار ━━━{C.RESET}")
        file_paths = {}
        for file, file_errors in by_file.items():
            fp = self._find_file(file)
            file_paths[file] = fp
            if fp and fp.exists():
                print(f"\n  {C.YELLOW}{C.BOLD}{fp.relative_to(self.path)}{C.RESET}")
                try:
                    lines = fp.read_text(encoding='utf-8', errors='ignore').split('\n')
                    error_lines = set(e["line"] for e in file_errors)
                    for ln in sorted(error_lines):
                        if 1 <= ln <= len(lines):
                            start = max(0, ln - 3)
                            end = min(len(lines), ln + 2)
                            for i in range(start, end):
                                marker = f"{C.RED}→{C.RESET}" if (i+1) == ln else " "
                                print(f"  {marker} {C.GRAY}{i+1:>4}{C.RESET}│ {lines[i]}")
                except Exception as e:
                    print(f"    {C.RED}خطا:{C.RESET} {e}")

        # رفع خودکار (فقط برای خطاهای امن)
        if fix:
            print(f"\n{C.CYAN}{C.BOLD}━━━ رفع خودکار ━━━{C.RESET}")
            fixed_count = 0
            for file, file_errors in by_file.items():
                fp = file_paths.get(file)
                if not fp or not fp.exists():
                    continue

                # فقط تبدیل .ts به .tsx (امن)
                if fp.suffix == '.ts':
                    has_jsx_error = any(
                        '>' in e["message"] or 'JSX' in e["message"]
                        for e in file_errors
                    )
                    if has_jsx_error:
                        content = fp.read_text(encoding='utf-8', errors='ignore')
                        if re.search(r'<\w+[> ]', content) or re.search(r'</\w+>', content):
                            new_path = fp.with_suffix('.tsx')
                            if not new_path.exists():
                                # backup قبل از تغییر
                                self._backup_file(fp)
                                fp.rename(new_path)
                                print(f"  {C.GREEN}✓{C.RESET} {fp.name} → {new_path.name}")
                                fixed_count += 1
                                continue

                # برای خطاهای آکولاد، فقط نمایش پیشنهاد (بدون تغییر خودکار)
                has_brace_error = any("'}' expected" in e["message"] for e in file_errors)
                if has_brace_error:
                    print(f"  {C.YELLOW}⚠{C.RESET} {fp.name}: نیاز به بررسی دستی (آکولاد)")
                    print(f"    {C.GRAY}→ python econojin.py phase3 --show {fp.name}{C.RESET}")

            if fixed_count:
                print(f"\n  {C.GREEN}✓ {fixed_count} مشکل رفع شد{C.RESET}")
            else:
                print(f"  {C.YELLOW}⚠ رفع خودکار انجام نشد - نیاز به بررسی دستی{C.RESET}")

            print(f"\n  {C.CYAN}برای برگرداندن:{C.RESET} python econojin.py phase3 --revert")
            print(f"  {C.CYAN}برای دیدن فایل:{C.RESET} python econojin.py phase3 --show FILENAME")

        # ذخیره گزارش
        report_path = self.path / 'analysis_reports'
        report_path.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_path / f"build_errors_{ts}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({"errors": errors, "count": len(errors), "returncode": returncode}, f, ensure_ascii=False, indent=2)
        print(f"\n  {C.GRAY}گزارش:{C.RESET} {report_file.name}")

        return True

    def _backup_file(self, fp):
        """backup فایل قبل از تغییر."""
        backup_dir = self.path / 'analysis_reports' / 'backups'
        backup_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{fp.stem}_{ts}{fp.suffix}"
        shutil.copy2(fp, backup_path)
        # ذخیره مسیر اصلی برای revert
        manifest = backup_dir / 'manifest.json'
        manifest_data = {}
        if manifest.exists():
            manifest_data = json.loads(manifest.read_text(encoding='utf-8'))
        manifest_data[str(fp)] = str(backup_path)
        manifest.write_text(json.dumps(manifest_data, indent=2), encoding='utf-8')

    def _revert_fixes(self):
        """برگرداندن تغییرات fix."""
        self._print_header("↩ برگرداندن تغییرات")
        backup_dir = self.path / 'analysis_reports' / 'backups'
        manifest = backup_dir / 'manifest.json'

        if not manifest.exists():
            print(f"\n  {C.YELLOW}هیچ backup ای وجود ندارد{C.RESET}")
            return True

        manifest_data = json.loads(manifest.read_text(encoding='utf-8'))
        print(f"\n  {C.CYAN}{len(manifest_data)} تغییر قابل برگرداندن:{C.RESET}\n")

        for original_path_str, backup_path_str in manifest_data.items():
            original = Path(original_path_str)
            backup = Path(backup_path_str)

            print(f"  {C.YELLOW}فایل اصلی:{C.RESET} {original.name}")

            # اگه فایل اصلی renamed شده (مثل .ts → .tsx)
            if not original.exists():
                # پیدا کردن فایل renamed
                renamed = original.with_suffix('.tsx') if original.suffix == '.ts' else None
                if renamed and renamed.exists():
                    print(f"  {C.GRAY}حذف:{C.RESET} {renamed.name}")
                    renamed.unlink()
                    print(f"  {C.GREEN}✓ برگرداندن:{C.RESET} {original.name}")
                    shutil.copy2(backup, original)
                else:
                    print(f"  {C.RED}✗ فایل اصلی پیدا نشد{C.RESET}")
            else:
                # فایل هنوز موجوده، فقط restore کن
                shutil.copy2(backup, original)
                print(f"  {C.GREEN}✓ برگردانده شد{C.RESET}")

        # پاک کردن manifest
        manifest.unlink()
        print(f"\n  {C.GREEN}✓ همه تغییرات برگردانده شد{C.RESET}")
        return True

    def _show_file_content(self, filename):
        """نمایش کامل محتوای یک فایل."""
        self._print_header(f"📄 محتوای فایل: {filename}")

        fp = self._find_file(filename)
        if not fp or not fp.exists():
            # تلاش با نام‌های مختلف
            for ext in ['.ts', '.tsx', '.py']:
                fp = self._find_file(filename + ext)
                if fp and fp.exists():
                    break

        if not fp or not fp.exists():
            print(f"\n  {C.RED}❌ فایل پیدا نشد: {filename}{C.RESET}")
            print(f"  {C.GRAY}مسیرهای بررسی شده:{C.RESET}")
            print(f"    • {self.path / filename}")
            print(f"    • {self.path / 'apps' / 'web' / filename}")
            return False

        print(f"\n  {C.CYAN}فایل:{C.RESET} {fp.relative_to(self.path)}")
        print(f"  {C.CYAN}حجم:{C.RESET} {self._h(fp.stat().st_size)}")

        try:
            content = fp.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            print(f"  {C.CYAN}خطوط:{C.RESET} {len(lines)}\n")
            print(f"{C.GRAY}{'─'*60}{C.RESET}")

            for i, line in enumerate(lines, 1):
                print(f"  {C.GRAY}{i:>4}{C.RESET}│ {line}")

            print(f"{C.GRAY}{'─'*60}{C.RESET}")
            print(f"\n  {C.CYAN}برای ویرایش:{C.RESET} code \"{fp}\"")
        except Exception as e:
            print(f"  {C.RED}خطا:{C.RESET} {e}")

        return True

    def _find_file(self, file):
        """پیدا کردن فایل واقعی."""
        fp = self.path / file
        if fp.exists():
            return fp
        fp = self.path / 'apps' / 'web' / file
        if fp.exists():
            return fp
        matches = list(self.path.glob(f'**/{Path(file).name}'))
        matches = [m for m in matches if not any(s in str(m) for s in SKIP_DIRS)]
        if matches:
            return matches[0]
        return None

    def status(self):
        self._print_header("📊 وضعیت پروژه")

        print(f"\n{C.CYAN}{C.BOLD}━━━ فایل‌های غیرضروری ━━━{C.RESET}")
        junk = 0
        for name in JUNK_FILES:
            if (self.path / name).exists():
                junk += 1; print(f"  {C.RED}✗{C.RESET} {name}")
        if junk == 0: print(f"  {C.GREEN}✓ تمیز{C.RESET}")

        print(f"\n{C.CYAN}{C.BOLD}━━━ پوشه‌های پشتیبان ━━━{C.RESET}")
        backup = 0
        for name in BACKUP_DIRS:
            if (self.path / name).exists():
                backup += 1; print(f"  {C.RED}✗{C.RESET} {name}/")
        if backup == 0: print(f"  {C.GREEN}✓ حذف شده‌اند{C.RESET}")

        print(f"\n{C.CYAN}{C.BOLD}━━━ cache ━━━{C.RESET}")
        cache = 0
        for name in CACHE_DIRS:
            if (self.path / name).exists():
                cache += 1; print(f"  {C.RED}✗{C.RESET} {name}/")
        if cache == 0: print(f"  {C.GREEN}✓ حذف شده‌اند{C.RESET}")

        print(f"\n{C.CYAN}{C.BOLD}━━━ محیط فعال ━━━{C.RESET}")
        venv = self.path / '.venv'
        if venv.exists():
            print(f"  {C.GREEN}✓ .venv/{C.RESET} ({self._h(self._dir_size(venv))})")
        else: print(f"  {C.YELLOW}⚠ .venv وجود ندارد{C.RESET}")

        print(f"\n{C.CYAN}{C.BOLD}━━━ فایل‌های بزرگ (>۱۵۰ خط) ━━━{C.RESET}")
        large = self._find_large_files(150)
        # فیلتر کردن فایل‌های اسکریپت خودمون
        large_filtered = [(fp, l) for fp, l in large if fp.name not in ['econojin.py', 'cleanup.py']]
        for fp, l in large_filtered[:5]:
            icon = "🔴" if l >= 500 else "🟠"
            print(f"  {icon} {l:>5}  {fp.relative_to(self.path)}")
        if len(large_filtered) > 5:
            print(f"  {C.GRAY}... و {len(large_filtered)-5} مورد دیگر{C.RESET}")

        print(f"\n{C.CYAN}{C.BOLD}━━━ Git ━━━{C.RESET}")
        code, out, _ = self._run_cmd("git status --short")
        if code == 0:
            changes = [l for l in out.split('\n') if l.strip()]
            print(f"  {C.CYAN}تغییرات:{C.RESET} {len(changes)}")
            code2, out2, _ = self._run_cmd("git log --oneline -3")
            if code2 == 0:
                for line in out2.split('\n')[:3]:
                    if line.strip(): print(f"    {C.GRAY}{line.strip()}{C.RESET}")

        print(f"\n{C.MAGENTA}{C.BOLD}{'━'*50}{C.RESET}")
        score = 100 - junk*5 - backup*10 - cache*5 - min(30, len(large_filtered)*2)
        score = max(0, score)
        if score >= 80: grade, color = "A", C.GREEN
        elif score >= 60: grade, color = "B", C.YELLOW
        else: grade, color = "C", C.RED
        print(f"  {C.CYAN}امتیاز:{C.RESET} {color}{C.BOLD}{score}/100 (نمره {grade}){C.RESET}")
        print()
        return True


def show_menu():
    print(f"""
{C.MAGENTA}{C.BOLD}╔{'═'*58}╗{C.RESET}
{C.MAGENTA}{C.BOLD}║  🚀 Econojin Master v3.4 - اسکریپت واحد{C.RESET}{' '*8}{C.MAGENTA}{C.BOLD}║{C.RESET}
{C.MAGENTA}{C.BOLD}╚{'═'*58}╝{C.RESET}

{C.CYAN}فازها:{C.RESET}
  {C.GREEN}phase0{C.RESET}             پاکسازی پروژه
  {C.GREEN}phase0 --execute{C.RESET}    اجرای پاکسازی
  {C.GREEN}phase1{C.RESET}             تحلیل refactor
  {C.GREEN}phase1 --execute{C.RESET}    تحلیل + template
  {C.GREEN}phase2{C.RESET}             لیست فایل‌های آماده refactor
  {C.GREEN}phase2 --file NAME --execute{C.RESET}  اجرای refactor
  {C.GREEN}phase3{C.RESET}             پیدا کردن خطاهای build
  {C.GREEN}phase3 --fix{C.RESET}       رفع خودکار خطاها
  {C.GREEN}status{C.RESET}             وضعیت پروژه

{C.YELLOW}مثال:{C.RESET}
  python econojin.py status
  python econojin.py phase3 --fix
  python econojin.py phase2 --file ProductionGIS --execute
""")


def main():
    C.enable_windows()
    if len(sys.argv) < 2:
        show_menu(); return

    parser = argparse.ArgumentParser(description='Econojin Master v3.5')
    parser.add_argument('command', choices=['phase0', 'phase1', 'phase2', 'phase3', 'status', 'all'])
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--fix', action='store_true', help='رفع خودکار خطاها در phase3')
    parser.add_argument('--revert', action='store_true', help='برگرداندن تغییرات fix در phase3')
    parser.add_argument('--show', type=str, help='نمایش کامل محتوای فایل در phase3')
    parser.add_argument('--file', type=str, help='نام فایل برای phase2')
    parser.add_argument('--threshold', type=int, default=150)

    args = parser.parse_args()
    master = EconojinMaster()

    if not master.path.exists():
        print(f"{C.RED}❌ مسیر وجود ندارد: {master.path}{C.RESET}"); sys.exit(1)

    if args.command == 'phase0':
        master.phase0(execute=args.execute)
    elif args.command == 'phase1':
        master.phase1(execute=args.execute, threshold=args.threshold)
    elif args.command == 'phase2':
        master.phase2(target_file=args.file, execute=args.execute)
    elif args.command == 'phase3':
        master.phase3(execute=args.execute, fix=args.fix, show_file=args.show, revert=args.revert)
    elif args.command == 'status':
        master.status()
    elif args.command == 'all':
        master.phase0(execute=args.execute)
        print(f"\n{C.GRAY}{'─'*50}{C.RESET}\n")
        master.phase1(execute=args.execute, threshold=args.threshold)
        print(f"\n{C.GRAY}{'─'*50}{C.RESET}\n")
        master.status()


if __name__ == '__main__':
    main()
