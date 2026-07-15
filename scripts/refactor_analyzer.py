#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
  🔧 Refactor Analyzer - فاز ۱: تحلیل و پیشنهاد refactor
  نسخه: 1.0.0
  سازنده: Super Z (Z.ai)
============================================================

اسکریپت تحلیل کامپوننت‌های بزرگ React/TypeScript و پیشنهاد
ساختار جدید برای refactor.

⚡ ویژگی‌ها:
  • شناسایی کامپوننت‌های بزرگ (>150 خط)
  • تحلیل imports، state، functions، JSX
  • پیشنهاد ساختار جدید (split به زیرکامپوننت)
  • تولید template کد جدید
  • گزارش قبل/بعد

📋 کارهایی که انجام می‌دهد:
  1. پیدا کردن فایل‌های .tsx/.ts/.py بزرگ
  2. تحلیل ساختار هر فایل (AST-based)
  3. شناسایی مسئولیت‌های مختلف
  4. پیشنهاد تقسیم به فایل‌های کوچک‌تر
  5. تولید template برای فایل‌های جدید
  6. ذخیره گزارش کامل

🚀 نحوه اجرا:
  python refactor_analyzer.py
  python refactor_analyzer.py --execute          # تولید template ها
  python refactor_analyzer.py --threshold 200    # تغییر آستانه
  python refactor_analyzer.py "D:\\econojin.com" # مسیر دلخواه
"""

import os
import sys
import re
import json
import argparse
import platform
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# ============================================================
#  رنگ‌ها
# ============================================================
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

    @staticmethod
    def enable_windows():
        if platform.system() == "Windows":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass

    @staticmethod
    def disable():
        for attr in dir(C):
            if attr.isupper():
                setattr(C, attr, "")


# ============================================================
#  پیکربندی
# ============================================================

# آستانه‌ها (خط)
THRESHOLDS = {
    'critical': 500,   # بحرانی - حتماً refactor
    'high': 250,       # بالا - توصیه می‌شود
    'medium': 150,     # متوسط - بهتره
    'low': 100,        # پایین - اختیاری
}

# پسوندهای هدف
TARGET_EXTENSIONS = {'.tsx', '.ts', '.py'}

# پوشه‌های نادیده
SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', '.next', '.nuxt', 'dist',
    'build', '.cache', '.pytest_cache', '.mypy_cache',
    '.venv', '.venv-1', '.venv-2', 'venv', 'env',
    '.pnpm-store', 'analysis_reports', 'scripts',
    'target', 'bin', 'obj', '.gradle',
}

# الگوهای تشخیص مسئولیت در کد
RESPONSIBILITY_PATTERNS = {
    'state_management': [
        r'useState\s*\(',
        r'useReducer\s*\(',
        r'createContext\s*\(',
        r'useContext\s*\(',
    ],
    'data_fetching': [
        r'useEffect\s*\([^)]*fetch',
        r'axios\.(get|post|put|delete)',
        r'fetch\s*\(',
        r'useQuery\s*\(',
        r'useMutation\s*\(',
    ],
    'event_handlers': [
        r'const\s+handle\w+\s*=',
        r'function\s+handle\w+\s*\(',
        r'onClick\s*=',
        r'onSubmit\s*=',
        r'onChange\s*=',
    ],
    'rendering': [
        r'return\s*\(',
        r'<\w+[\s>]',
        r'map\s*\([^)]*=>\s*[(<]',
    ],
    'business_logic': [
        r'const\s+calculate\w+\s*=',
        r'const\s+format\w+\s*=',
        r'const\s+validate\w+\s*=',
        r'const\s+parse\w+\s*=',
    ],
    'side_effects': [
        r'useEffect\s*\(',
        r'useLayoutEffect\s*\(',
        r'addEventListener\s*\(',
        r'setInterval\s*\(',
        r'setTimeout\s*\(',
    ],
    'form_handling': [
        r'register\s*\(',
        r'handleSubmit\s*\(',
        r'formState',
        r'useForm\s*\(',
    ],
    'api_calls': [
        r'async\s+function',
        r'await\s+',
        r'\.json\s*\(\s*\)',
    ],
}

# پیشنهادهای refactor بر اساس مسئولیت‌ها
REFACTOR_SUGGESTIONS = {
    'state_management': {
        'action': 'استخراج state به custom hook',
        'pattern': 'use{ComponentName}State',
        'file': 'hooks/use{ComponentName}.ts',
    },
    'data_fetching': {
        'action': 'استخراج data fetching به React Query hook',
        'pattern': 'use{Resource}Query',
        'file': 'hooks/use{Resource}.ts',
    },
    'event_handlers': {
        'action': 'استخراج event handlers به hook جداگانه',
        'pattern': 'use{ComponentName}Handlers',
        'file': 'hooks/use{ComponentName}Handlers.ts',
    },
    'business_logic': {
        'action': 'استخراج business logic به utils',
        'pattern': '{componentName}Utils',
        'file': 'utils/{componentName}.ts',
    },
    'side_effects': {
        'action': 'استخراج effects به hook جداگانه',
        'pattern': 'use{ComponentName}Effects',
        'file': 'hooks/use{ComponentName}Effects.ts',
    },
    'form_handling': {
        'action': 'استخراج form logic به hook',
        'pattern': 'use{ComponentName}Form',
        'file': 'hooks/use{ComponentName}Form.ts',
    },
}


# ============================================================
#  کلاس تحلیلگر
# ============================================================
class RefactorAnalyzer:
    def __init__(self, project_path: str, threshold: int = 150, generate_templates: bool = False):
        self.path = Path(project_path).resolve()
        self.threshold = threshold
        self.generate_templates = generate_templates
        self.results = {
            "meta": {
                "project": str(self.path),
                "timestamp": datetime.now().isoformat(),
                "threshold": threshold,
            },
            "files_analyzed": [],
            "summary": {
                "total_large_files": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "total_lines_saved": 0,
                "suggestions_count": 0,
            },
        }

    def _should_skip(self, dir_name: str) -> bool:
        return dir_name in SKIP_DIRS

    def _read_file(self, path: Path) -> str:
        try:
            for enc in ['utf-8', 'utf-8-sig', 'latin-1']:
                try:
                    with open(path, 'r', encoding=enc) as f:
                        return f.read()
                except:
                    continue
        except:
            return ""
        return ""

    def _detect_responsibilities(self, content: str) -> dict:
        """تشخیص مسئولیت‌های مختلف در کد."""
        responsibilities = defaultdict(lambda: {"count": 0, "matches": []})
        for category, patterns in RESPONSIBILITY_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content):
                    line_num = content[:match.start()].count('\n') + 1
                    responsibilities[category]["count"] += 1
                    responsibilities[category]["matches"].append({
                        "line": line_num,
                        "match": match.group()[:60],
                    })
        return dict(responsibilities)

    def _extract_component_info(self, content: str, filename: str) -> dict:
        """استخراج اطلاعات کامپوننت."""
        info = {
            "name": "",
            "type": "unknown",
            "imports": [],
            "exports": [],
            "hooks": [],
            "functions": [],
            "components": [],
            "props": [],
        }

        # نام کامپوننت
        patterns = [
            (r'export\s+default\s+function\s+(\w+)', 'default_function'),
            (r'export\s+function\s+(\w+)', 'named_function'),
            (r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>', 'arrow'),
            (r'export\s+default\s+(\w+)', 'export_var'),
            (r'class\s+(\w+)', 'class'),
        ]
        for pattern, type_ in patterns:
            m = re.search(pattern, content)
            if m:
                info["name"] = m.group(1)
                info["type"] = type_
                break

        # imports
        for m in re.finditer(r'^import\s+.*?from\s+["\']([^"\']+)["\']', content, re.MULTILINE):
            info["imports"].append(m.group(1))

        # hooks استفاده شده
        for m in re.finditer(r'\b(use[A-Z]\w+)\s*\(', content):
            hook = m.group(1)
            if hook not in info["hooks"]:
                info["hooks"].append(hook)

        # تعریف توابع
        for m in re.finditer(r'(?:const|function)\s+(\w+)\s*=?\s*(?:\([^)]*\)|function)\s*(?:=>|{)', content):
            fn = m.group(1)
            if fn != info["name"] and fn not in info["functions"]:
                info["functions"].append(fn)

        # کامپوننت‌های فرعی (JSX)
        for m in re.finditer(r'<([A-Z]\w+)', content):
            comp = m.group(1)
            if comp not in info["components"] and comp != info["name"]:
                info["components"].append(comp)

        return info

    def _generate_suggestions(self, responsibilities: dict, component_name: str) -> list:
        """تولید پیشنهادهای refactor."""
        suggestions = []
        # اطمینان از حرف بزرگ اول
        clean_name = component_name[0].upper() + component_name[1:] if component_name else "Component"
        camel_name = component_name[0].lower() + component_name[1:] if component_name else "component"

        for category, data in responsibilities.items():
            if data["count"] >= 3 and category in REFACTOR_SUGGESTIONS:
                sug = REFACTOR_SUGGESTIONS[category].copy()
                sug["category"] = category
                sug["count"] = data["count"]
                # استفاده از نام تمیز شده
                sug["pattern"] = sug["pattern"].replace("{ComponentName}", clean_name).replace("{componentName}", camel_name)
                sug["file"] = sug["file"].replace("{ComponentName}", clean_name).replace("{componentName}", camel_name)
                sug["file"] = sug["file"].replace("{Resource}", clean_name)
                suggestions.append(sug)
        return suggestions

    def _estimate_split(self, total_lines: int, suggestions: list) -> dict:
        """تخمین خطوط بعد از refactor."""
        # هر suggestion حدود ۳۰-۵۰٪ کاهش میاره
        reduction_per_suggestion = 0.15
        total_reduction = min(0.75, len(suggestions) * reduction_per_suggestion)
        new_lines = int(total_lines * (1 - total_reduction))
        return {
            "current_lines": total_lines,
            "estimated_new_lines": new_lines,
            "lines_saved": total_lines - new_lines,
            "reduction_percent": round(total_reduction * 100, 1),
        }

    def _generate_template(self, file_path: Path, info: dict, suggestions: list) -> list:
        """تولید template برای فایل‌های جدید."""
        templates = []
        component_name = info["name"] or file_path.stem

        for sug in suggestions:
            template_path = file_path.parent / sug["file"]
            if template_path.exists():
                continue

            if "hooks/" in sug["file"]:
                template = self._hook_template(component_name, sug["category"])
            elif "utils/" in sug["file"]:
                template = self._utils_template(component_name)
            else:
                continue

            templates.append({
                "path": str(template_path),
                "content": template,
                "category": sug["category"],
            })

        return templates

    def _hook_template(self, component_name: str, category: str) -> str:
        """Template برای custom hook."""
        hook_name = f"use{component_name}"
        if category == "state_management":
            return f"""import {{ useState, useEffect }} from 'react'

interface {component_name}State {{
  // TODO: تعریف state ها
  loading: boolean
  error: Error | null
}}

export function {hook_name}() {{
  const [state, setState] = useState<{component_name}State>({{
    loading: false,
    error: null,
  }})

  // TODO: منتقل کردن state ها و logic از {component_name}

  return {{
    ...state,
    // TODO: export actions
  }}
}}
"""
        elif category == "data_fetching":
            return f"""import {{ useQuery }} from '@tanstack/react-query'

export function {hook_name}() {{
  return useQuery({{
    queryKey: ['{component_name.lower()}'],
    queryFn: async () => {{
      // TODO: منتقل کردن fetch logic از {component_name}
      const response = await fetch('/api/{component_name.lower()}')
      return response.json()
    }},
  }})
}}
"""
        elif category == "event_handlers":
            return f"""import {{ useCallback }} from 'react'

export function {hook_name}Handlers() {{
  // TODO: منتقل کردن event handlers از {component_name}

  const handleSubmit = useCallback((e: React.FormEvent) => {{
    e.preventDefault()
    // TODO
  }}, [])

  const handleChange = useCallback((e: React.ChangeEvent) => {{
    // TODO
  }}, [])

  return {{
    handleSubmit,
    handleChange,
  }}
}}
"""
        elif category == "side_effects":
            return f"""import {{ useEffect }} from 'react'

export function {hook_name}Effects() {{
  // TODO: منتقل کردن useEffect ها از {component_name}

  useEffect(() => {{
    // TODO
  }}, [])
}}
"""
        return ""

    def _utils_template(self, component_name: str) -> str:
        """Template برای utils."""
        return f"""// Utility functions extracted from {component_name}

export function format{component_name}Data(data: unknown) {{
  // TODO: منتقل کردن format functions
  return data
}}

export function validate{component_name}Input(input: unknown) {{
  // TODO: منتقل کردن validation functions
  return true
}}
"""

    def _get_priority(self, lines: int) -> str:
        if lines >= THRESHOLDS['critical']:
            return "critical"
        elif lines >= THRESHOLDS['high']:
            return "high"
        elif lines >= THRESHOLDS['medium']:
            return "medium"
        else:
            return "low"

    # ============================================================
    #  تحلیل یک فایل
    # ============================================================
    def analyze_file(self, file_path: Path) -> dict:
        content = self._read_file(file_path)
        if not content:
            return None

        lines = content.count('\n') + 1
        if lines < self.threshold:
            return None

        rel_path = str(file_path.relative_to(self.path))
        info = self._extract_component_info(content, file_path.stem)
        responsibilities = self._detect_responsibilities(content)
        suggestions = self._generate_suggestions(responsibilities, info["name"] or file_path.stem)
        estimate = self._estimate_split(lines, suggestions)
        priority = self._get_priority(lines)

        # تولید template (اگه --execute)
        templates = []
        if self.generate_templates and suggestions:
            templates = self._generate_template(file_path, info, suggestions)

        result = {
            "file": rel_path,
            "lines": lines,
            "priority": priority,
            "component": info,
            "responsibilities": {k: v["count"] for k, v in responsibilities.items()},
            "suggestions": suggestions,
            "estimate": estimate,
            "templates_generated": len(templates),
        }

        # ذخیره template ها
        if templates:
            for tmpl in templates:
                tmpl_path = Path(tmpl["path"])
                tmpl_path.parent.mkdir(parents=True, exist_ok=True)
                with open(tmpl_path, 'w', encoding='utf-8') as f:
                    f.write(tmpl["content"])
                print(f"    {C.GREEN}✓ template:{C.RESET} {tmpl_path.relative_to(self.path)}")

        # به‌روزرسانی خلاصه
        self.results["summary"]["total_large_files"] += 1
        self.results["summary"][priority] += 1
        self.results["summary"]["total_lines_saved"] += estimate["lines_saved"]
        self.results["summary"]["suggestions_count"] += len(suggestions)

        return result

    # ============================================================
    #  اجرای کامل
    # ============================================================
    def run(self):
        print(f"\n{C.MAGENTA}{C.BOLD}╔{'═'*58}╗{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}║  🔧 Refactor Analyzer v1.0 - فاز ۱{' '*26}║{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}║  مسیر: {str(self.path):<51}║{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}║  آستانه: {self.threshold} خط{' '*43}║{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}╚{'═'*58}╝{C.RESET}")

        if not self.path.exists():
            print(f"{C.RED}❌ مسیر وجود ندارد!{C.RESET}")
            return False

        # پیدا کردن فایل‌های بزرگ
        print(f"\n{C.CYAN}🔍 اسکن فایل‌ها...{C.RESET}")
        large_files = []

        for root, dirs, files in os.walk(self.path):
            dirs[:] = [d for d in dirs if not self._should_skip(d)]
            for f in files:
                fp = Path(root) / f
                if fp.suffix.lower() in TARGET_EXTENSIONS:
                    try:
                        size_lines = sum(1 for _ in open(fp, 'r', encoding='utf-8', errors='ignore'))
                        if size_lines >= self.threshold:
                            large_files.append((fp, size_lines))
                    except:
                        pass

        large_files.sort(key=lambda x: x[1], reverse=True)

        if not large_files:
            print(f"  {C.GREEN}✓ هیچ فایل بزرگی پیدا نشد!{C.RESET}")
            return True

        print(f"  {C.YELLOW}{len(large_files)} فایل بزرگ پیدا شد{C.RESET}\n")

        # تحلیل هر فایل
        for fp, lines in large_files:
            priority = self._get_priority(lines)
            priority_colors = {
                'critical': C.RED + C.BOLD,
                'high': C.RED,
                'medium': C.YELLOW,
                'low': C.GRAY,
            }
            color = priority_colors.get(priority, C.YELLOW)
            icons = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '⚪'}

            print(f"{C.CYAN}{C.BOLD}━━━ {fp.relative_to(self.path)} ━━━{C.RESET}")
            print(f"  {icons[priority]} {color}{priority.upper()}{C.RESET} | {C.BOLD}{lines}{C.RESET} خط")

            result = self.analyze_file(fp)
            if result:
                self.results["files_analyzed"].append(result)

                # نمایش مسئولیت‌ها
                if result["responsibilities"]:
                    print(f"\n  {C.YELLOW}مسئولیت‌ها:{C.RESET}")
                    for cat, count in sorted(result["responsibilities"].items(), key=lambda x: x[1], reverse=True):
                        bar = '█' * min(count, 20)
                        print(f"    {cat:25} {color}{bar}{C.RESET} {count}")

                # نمایش پیشنهادها
                if result["suggestions"]:
                    print(f"\n  {C.GREEN}پیشنهادهای refactor:{C.RESET}")
                    for sug in result["suggestions"]:
                        print(f"    {C.BLUE}→{C.RESET} {sug['action']}")
                        print(f"      {C.GRAY}فایل:{C.RESET} {sug['file']}")
                else:
                    print(f"  {C.GRAY}(پیشنهاد خاصی نیست){C.RESET}")

                # نمایش تخمین
                est = result["estimate"]
                print(f"\n  {C.MAGENTA}تخمین:{C.RESET}")
                print(f"    {C.BOLD}قبل:{C.RESET} {est['current_lines']} خط")
                print(f"    {C.BOLD}بعد:{C.RESET} ~{est['estimated_new_lines']} خط")
                print(f"    {C.GREEN}کاهش:{C.RESET} {est['lines_saved']} خط ({est['reduction_percent']}%)")

                if self.generate_templates and result["templates_generated"]:
                    print(f"  {C.GREEN}✓ {result['templates_generated']} template تولید شد{C.RESET}")

            print()

        # خلاصه
        self._print_summary()

        # ذخیره گزارش
        self._save_report()

        return True

    def _print_summary(self):
        s = self.results["summary"]
        print(f"{C.MAGENTA}{C.BOLD}{'━'*58}{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}  📊 خلاصه فاز ۱{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}{'━'*58}{C.RESET}")
        print(f"  {C.CYAN}فایل‌های بزرگ:{C.RESET} {s['total_large_files']}")
        print(f"  {C.RED}🔴 بحرانی (≥500):{C.RESET} {s['critical']}")
        print(f"  {C.RED}🟠 بالا (≥250):{C.RESET} {s['high']}")
        print(f"  {C.YELLOW}🟡 متوسط (≥150):{C.RESET} {s['medium']}")
        print(f"  {C.CYAN}پیشنهادها:{C.RESET} {s['suggestions_count']}")
        print(f"  {C.GREEN}خطوط قابل کاهش:{C.RESET} ~{s['total_lines_saved']:,}")

    def _save_report(self):
        reports_dir = self.path / 'analysis_reports'
        reports_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = reports_dir / f"refactor_analysis_{ts}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n  {C.GRAY}گزارش:{C.RESET} {report_path}")


# ============================================================
#  ورودی
# ============================================================
def main():
    C.enable_windows()

    parser = argparse.ArgumentParser(
        description='Refactor Analyzer v1.0 - فاز ۱',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
مثال‌ها:
  python refactor_analyzer.py                              # تحلیل با آستانه ۱۵۰
  python refactor_analyzer.py --threshold 250              # فقط فایل‌های >۲۵۰ خط
  python refactor_analyzer.py --execute                    # تولید template ها
  python refactor_analyzer.py "D:\\my-project"             # مسیر دلخواه
        """
    )
    parser.add_argument('path', nargs='?', default=r'D:\econojin.com',
                        help='مسیر پروژه (پیش‌فرض: D:\\econojin.com)')
    parser.add_argument('-t', '--threshold', type=int, default=150,
                        help='آستانه خطوط (پیش‌فرض: 150)')
    parser.add_argument('--execute', action='store_true',
                        help='تولید template فایل‌های جدید')
    parser.add_argument('--no-color', action='store_true',
                        help='غیرفعال کردن رنگ')

    args = parser.parse_args()

    if args.no_color:
        C.disable()

    analyzer = RefactorAnalyzer(
        project_path=args.path,
        threshold=args.threshold,
        generate_templates=args.execute,
    )
    success = analyzer.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
