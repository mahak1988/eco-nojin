#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
analyze_apps.py — تحلیل جامع دایرکتوری apps/ + پیشنهادهای ارتقا
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• ساختار و آمار فایل‌ها
• پیچیدگی سایکلوماتیک
• کیفیت کد (type hints, docstrings, error handling)
• امنیت (hardcoded secrets, unsafe patterns)
• تست‌ها و پوشش
• وابستگی‌ها
• پیشنهادهای ارتقا
'''
from __future__ import annotations

import ast
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APPS = ROOT / 'apps'

# ── آستانه‌ها ──
MAX_COMPLEXITY = 15       # پیچیدگی سایکلوماتیک قابل قبول
MAX_FILE_LINES = 400      # حداکثر خطوط فایل
MAX_FUNC_LINES = 50       # حداکثر خطوط تابع
MIN_DOCSTRING_RATIO = 0.3 # حداقل نسبت docstring
MIN_TYPE_HINT_RATIO = 0.5 # حداقل نسبت type hints


# ═══════════════════════════════════════════════════════════
#  ۱. تحلیل ساختار
# ═══════════════════════════════════════════════════════════

def analyze_structure() -> dict:
    stats = defaultdict(lambda: {'files': 0, 'lines': 0, 'dirs': set()})
    all_files = []

    for ext in ('*.py', '*.ts', '*.tsx', '*.js', '*.jsx', '*.json',
                '*.yml', '*.yaml', '*.md', '*.sql', '*.css', '*.html'):
        for f in APPS.rglob(ext):
            if any(skip in str(f).replace('\\', '/') for skip in
                   ('node_modules', '__pycache__', '.pnpm-store',
                    'dist', 'build', '.next', 'locales_old_backup')):
                continue
            rel = f.relative_to(ROOT)
            parts = rel.parts
            app_name = parts[1] if len(parts) > 1 else 'root'
            try:
                lines = len(f.read_text(encoding='utf-8', errors='ignore').splitlines())
            except OSError:
                lines = 0
            stats[app_name]['files'] += 1
            stats[app_name]['lines'] += lines
            stats[app_name]['dirs'].add(str(rel.parent))
            all_files.append({
                'path': str(rel),
                'app': app_name,
                'ext': f.suffix,
                'lines': lines,
                'size_kb': round(f.stat().st_size / 1024, 1),
            })

    return {'stats': dict(stats), 'files': all_files}


# ═══════════════════════════════════════════════════════════
#  ۲. تحلیل پیچیدگی سایکلوماتیک (Python)
# ═══════════════════════════════════════════════════════════

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self._complexity = 0
        self._current_func = None

    def _count_complexity(self, node: ast.AST) -> int:
        count = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                  ast.ExceptHandler, ast.With, ast.AsyncWith,
                                  ast.Assert, ast.comprehension)):
                count += 1
            elif isinstance(child, ast.BoolOp):
                count += len(child.values) - 1
            elif isinstance(child, ast.IfExp):
                count += 1
        return count

    def visit_FunctionDef(self, node: ast.FunctionDef):
        complexity = self._count_complexity(node)
        self.functions.append({
            'name': node.name,
            'line': node.lineno,
            'lines': node.end_lineno - node.lineno + 1 if node.end_lineno else 0,
            'complexity': complexity,
            'args': len(node.args.args),
            'has_docstring': bool(ast.get_docstring(node)),
            'has_return_type': node.returns is not None,
            'has_type_hints': any(a.annotation for a in node.args.args),
        })
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef


def analyze_complexity() -> dict:
    results = []
    for f in APPS.rglob('*.py'):
        if any(skip in str(f).replace('\\', '/') for skip in
               ('node_modules', '__pycache__', 'tests', 'test_', 'conftest')):
            continue
        try:
            tree = ast.parse(f.read_text(encoding='utf-8', errors='ignore'))
        except SyntaxError:
            continue
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        for func in visitor.functions:
            func['file'] = str(f.relative_to(ROOT))
            results.append(func)

    # مرتب‌سازی بر اساس پیچیدگی
    results.sort(key=lambda x: x['complexity'], reverse=True)
    return {
        'total_functions': len(results),
        'high_complexity': [f for f in results if f['complexity'] > MAX_COMPLEXITY],
        'long_functions': [f for f in results if f['lines'] > MAX_FUNC_LINES],
        'top_20': results[:20],
    }


# ═══════════════════════════════════════════════════════════
#  ۳. تحلیل کیفیت کد (Python)
# ═══════════════════════════════════════════════════════════

def analyze_quality() -> dict:
    metrics = {
        'total_files': 0,
        'files_with_docstring': 0,
        'files_with_type_hints': 0,
        'files_with_error_handling': 0,
        'files_with_logging': 0,
        'bare_except': [],
        'todo_fixme': [],
        'print_statements': [],
        'no_docstring_funcs': 0,
        'total_funcs': 0,
    }

    for f in APPS.rglob('*.py'):
        if any(skip in str(f).replace('\\', '/') for skip in
               ('node_modules', '__pycache__', 'tests', 'test_', 'conftest')):
            continue
        try:
            text = f.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(text)
        except (SyntaxError, OSError):
            continue

        metrics['total_files'] += 1
        rel = str(f.relative_to(ROOT))

        # docstring ماژول
        if ast.get_docstring(tree):
            metrics['files_with_docstring'] += 1

        # type hints
        has_hints = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics['total_funcs'] += 1
                if not ast.get_docstring(node):
                    metrics['no_docstring_funcs'] += 1
                if node.returns or any(a.annotation for a in node.args.args):
                    has_hints = True
        if has_hints:
            metrics['files_with_type_hints'] += 1

        # error handling
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                metrics['files_with_error_handling'] += 1
                break

        # logging
        if 'logging' in text or 'logger' in text or 'structlog' in text:
            metrics['files_with_logging'] += 1

        # bare except
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                metrics['bare_except'].append(f'{rel}:{node.lineno}')

        # TODO/FIXME
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(r'\b(TODO|FIXME|HACK|XXX|BUG)\b', line, re.IGNORECASE):
                metrics['todo_fixme'].append(f'{rel}:{i}: {line.strip()[:80]}')

        # print statements (به جای logging)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'print':
                    metrics['print_statements'].append(f'{rel}:{node.lineno}')

    return metrics


# ═══════════════════════════════════════════════════════════
#  ۴. تحلیل امنیت
# ═══════════════════════════════════════════════════════════

def analyze_security() -> dict:
    issues = []
    patterns = [
        (r'(?i)(password|secret|api_key|token)\s*=\s*["\'][^"\']{4,}["\']',
         'hardcoded-secret', 'high'),
        (r'(?i)eval\s*\(', 'eval-usage', 'high'),
        (r'(?i)exec\s*\(', 'exec-usage', 'high'),
        (r'(?i)os\.system\s*\(', 'os-system', 'medium'),
        (r'(?i)subprocess\.call\s*\([^)]*shell\s*=\s*True', 'shell-injection', 'high'),
        (r'(?i)pickle\.loads?\s*\(', 'unsafe-deserialization', 'medium'),
        (r'(?i)yaml\.load\s*\([^)]*Loader\s*=\s*yaml\.Loader', 'unsafe-yaml', 'medium'),
        (r'(?i)random\.(randint|choice|random)\s*\(', 'weak-random', 'low'),
        (r'(?i)hashlib\.md5\s*\(', 'weak-hash-md5', 'medium'),
        (r'(?i)hashlib\.sha1\s*\(', 'weak-hash-sha1', 'low'),
        (r'(?i)verify\s*=\s*False', 'tls-disabled', 'medium'),
        (r'(?i)debug\s*=\s*True', 'debug-mode', 'medium'),
    ]

    for f in APPS.rglob('*.py'):
        if any(skip in str(f).replace('\\', '/') for skip in
               ('node_modules', '__pycache__', 'tests', 'test_', 'conftest')):
            continue
        try:
            text = f.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        rel = str(f.relative_to(ROOT))
        for i, line in enumerate(text.splitlines(), 1):
            for pat, name, severity in patterns:
                if re.search(pat, line):
                    issues.append({
                        'file': rel, 'line': i,
                        'issue': name, 'severity': severity,
                        'snippet': line.strip()[:100],
                    })

    return {'total': len(issues), 'issues': issues}


# ═══════════════════════════════════════════════════════════
#  ۵. تحلیل تست‌ها
# ═══════════════════════════════════════════════════════════

def analyze_tests() -> dict:
    test_files = []
    source_files = []

    for f in APPS.rglob('*.py'):
        if any(skip in str(f).replace('\\', '/') for skip in ('node_modules', '__pycache__')):
            continue
        rel = str(f.relative_to(ROOT))
        if 'test' in f.name.lower() or '/tests/' in rel:
            test_files.append(rel)
        elif f.suffix == '.py':
            source_files.append(rel)

    # نسبت تست به کد
    ratio = len(test_files) / max(len(source_files), 1)

    return {
        'test_files': len(test_files),
        'source_files': len(source_files),
        'test_ratio': round(ratio, 3),
        'test_files_list': test_files[:20],
        'apps_without_tests': [],
    }


# ═══════════════════════════════════════════════════════════
#  ۶. تحلیل وابستگی‌ها
# ═══════════════════════════════════════════════════════════

def analyze_dependencies() -> dict:
    deps = {'npm': {}, 'pypi': {}}

    # npm
    for pkg in APPS.rglob('package.json'):
        if 'node_modules' in str(pkg):
            continue
        try:
            data = json.loads(pkg.read_text(encoding='utf-8'))
            rel_parts = pkg.relative_to(ROOT).parts
            app = rel_parts[1] if len(rel_parts) > 1 else 'root'
            for section in ('dependencies', 'devDependencies'):
                for name, ver in data.get(section, {}).items():
                    if name not in deps['npm']:
                        deps['npm'][name] = {'version': ver, 'apps': []}
                    deps['npm'][name]['apps'].append(app)
        except (json.JSONDecodeError, OSError):
            continue

    # PyPI
    for req in APPS.rglob('requirements.txt'):
        if 'node_modules' in str(req):
            continue
        try:
            for line in req.read_text(encoding='utf-8').splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    name = re.split(r'[=<>!\[]', line)[0].strip()
                    if name:
                        deps['pypi'][name] = {'spec': line}
        except OSError:
            continue

    return deps


# ═══════════════════════════════════════════════════════════
#  ۷. تولید پیشنهادهای ارتقا
# ═══════════════════════════════════════════════════════════

def generate_recommendations(structure, complexity, quality, security,
                             tests, deps) -> list[dict]:
    recs = []

    # ── پیچیدگی ──
    if complexity['high_complexity']:
        recs.append({
            'priority': 'high',
            'category': 'معماری',
            'title': f"کاهش پیچیدگی {len(complexity['high_complexity'])} تابع",
            'detail': 'توابع با پیچیدگی >۱۵ باید به توابع کوچک‌تر تقسیم شوند. '
                      'از الگوهای Strategy، Command یا Pipeline استفاده کنید.',
            'files': [f['file'] for f in complexity['high_complexity'][:5]],
        })

    if complexity['long_functions']:
        recs.append({
            'priority': 'medium',
            'category': 'معماری',
            'title': f"کوتاه‌کردن {len(complexity['long_functions'])} تابع بلند",
            'detail': f'توابع با بیش از {MAX_FUNC_LINES} خط باید شکسته شوند. '
                      'هر تابع باید یک مسئولیت داشته باشد (SRP).',
        })

    # ── کیفیت کد ──
    doc_ratio = quality['files_with_docstring'] / max(quality['total_files'], 1)
    if doc_ratio < MIN_DOCSTRING_RATIO:
        recs.append({
            'priority': 'medium',
            'category': 'مستندسازی',
            'title': f'افزایش docstring (فعلاً {doc_ratio:.0%})',
            'detail': 'همه ماژول‌ها و توابع عمومی باید docstring داشته باشند. '
                      'از فرمت Google یا NumPy استفاده کنید.',
        })

    hint_ratio = quality['files_with_type_hints'] / max(quality['total_files'], 1)
    if hint_ratio < MIN_TYPE_HINT_RATIO:
        recs.append({
            'priority': 'medium',
            'category': 'کیفیت کد',
            'title': f'افزایش type hints (فعلاً {hint_ratio:.0%})',
            'detail': 'Type hints باعث کشف زودتر باگ‌ها و بهبود IDE support می‌شود. '
                      'از mypy برای بررسی خودکار استفاده کنید.',
        })

    if quality['bare_except']:
        recs.append({
            'priority': 'high',
            'category': 'مدیریت خطا',
            'title': f'حذف {len(quality["bare_except"])} bare except',
            'detail': 'bare except همه خطاها (حتی KeyboardInterrupt) را می‌گیرد. '
                      'به جای آن Exception یا خطای خاص را catch کنید.',
            'files': quality['bare_except'][:5],
        })

    if quality['print_statements']:
        recs.append({
            'priority': 'low',
            'category': 'Logging',
            'title': f'جایگزینی {len(quality["print_statements"])} print با logging',
            'detail': 'از structlog یا logging استاندارد استفاده کنید. '
                      'print در production قابل فیلتر و جستجو نیست.',
        })

    if quality['todo_fixme']:
        recs.append({
            'priority': 'low',
            'category': 'بدهی فنی',
            'title': f'بررسی {len(quality["todo_fixme"])} TODO/FIXME',
            'detail': 'هر TODO باید یک issue متناظر در GitHub داشته باشد.',
        })

    # ── امنیت ──
    high_sec = [i for i in security['issues'] if i['severity'] == 'high']
    if high_sec:
        recs.append({
            'priority': 'critical',
            'category': 'امنیت',
            'title': f'رفع {len(high_sec)} مشکل امنیتی بحرانی',
            'detail': 'eval/exec/os.system/shell=True باید حذف یا محدود شوند.',
            'files': [f"{i['file']}:{i['line']}" for i in high_sec[:5]],
        })

    # ── تست ──
    if tests['test_ratio'] < 0.1:
        recs.append({
            'priority': 'high',
            'category': 'تست',
            'title': f'افزایش پوشش تست (فعلاً {tests["test_ratio"]:.1%})',
            'detail': 'حداقل ۳۰٪ فایل‌های source باید تست داشته باشند. '
                      'از pytest + httpx برای API testing استفاده کنید.',
        })

    # ── وابستگی‌ها ──
    if len(deps['npm']) > 50:
        recs.append({
            'priority': 'low',
            'category': 'وابستگی‌ها',
            'title': f'بررسی {len(deps["npm"])} وابستگی npm',
            'detail': 'وابستگی‌های تکراری بین apps را با workspace hoisting کاهش دهید. '
                      'از pnpm workspace استفاده کنید.',
        })

    # ── ساختار ──
    large_files = [f for f in structure['files'] if f['lines'] > MAX_FILE_LINES]
    if large_files:
        recs.append({
            'priority': 'medium',
            'category': 'معماری',
            'title': f'شکستن {len(large_files)} فایل بزرگ (>{MAX_FILE_LINES} خط)',
            'detail': 'فایل‌های بزرگ را به ماژول‌های کوچک‌تر تقسیم کنید.',
            'files': [f['path'] for f in large_files[:5]],
        })

    # مرتب‌سازی بر اساس اولویت
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    recs.sort(key=lambda r: priority_order.get(r['priority'], 9))
    return recs


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════

def main() -> int:
    print('═' * 60)
    print('  🔬 تحلیل جامع apps/ — econojin.com')
    print('═' * 60)

    # ۱. ساختار
    print('\n  [۱] تحلیل ساختار …')
    structure = analyze_structure()
    print(f'     {len(structure["files"])} فایل در {len(structure["stats"])} اپ')
    for app, s in sorted(structure['stats'].items(),
                         key=lambda x: x[1]['lines'], reverse=True):
        print(f'     📁 {app}: {s["files"]} فایل / {s["lines"]:,} خط')

    # ۲. پیچیدگی
    print('\n  [۲] تحلیل پیچیدگی …')
    complexity = analyze_complexity()
    print(f'     {complexity["total_functions"]} تابع')
    print(f'     ⚠️  {len(complexity["high_complexity"])} تابع با پیچیدگی >{MAX_COMPLEXITY}')
    print(f'     ⚠️  {len(complexity["long_functions"])} تابع با >{MAX_FUNC_LINES} خط')
    if complexity['top_20']:
        print('\n     پیچیده‌ترین توابع:')
        for f in complexity['top_20'][:10]:
            flag = '🔴' if f['complexity'] > MAX_COMPLEXITY else '🟡'
            print(f'     {flag} {f["complexity"]:>3} | {f["lines"]:>4} خط | '
                  f'{f["file"]}:{f["line"]} → {f["name"]}()')

    # ۳. کیفیت
    print('\n  [۳] تحلیل کیفیت …')
    quality = analyze_quality()
    doc_r = quality['files_with_docstring'] / max(quality['total_files'], 1)
    hint_r = quality['files_with_type_hints'] / max(quality['total_files'], 1)
    log_r = quality['files_with_logging'] / max(quality['total_files'], 1)
    print(f'     📄 {quality["total_files"]} فایل Python')
    print(f'     📝 docstring: {doc_r:.0%}')
    print(f'     🔤 type hints: {hint_r:.0%}')
    print(f'     📊 logging: {log_r:.0%}')
    print(f'     ⚠️  bare except: {len(quality["bare_except"])}')
    print(f'     ⚠️  print: {len(quality["print_statements"])}')
    print(f'     📋 TODO/FIXME: {len(quality["todo_fixme"])}')

    # ۴. امنیت
    print('\n  [۴] تحلیل امنیت …')
    security = analyze_security()
    print(f'     {security["total"]} یافته')
    by_sev = defaultdict(int)
    for i in security['issues']:
        by_sev[i['severity']] += 1
    for sev in ('high', 'medium', 'low'):
        if by_sev[sev]:
            print(f'     {"🔴" if sev=="high" else "🟡" if sev=="medium" else "🔵"} '
                  f'{sev}: {by_sev[sev]}')

    # ۵. تست‌ها
    print('\n  [۵] تحلیل تست‌ها …')
    tests = analyze_tests()
    print(f'     🧪 {tests["test_files"]} فایل تست / {tests["source_files"]} فایل source')
    print(f'     📊 نسبت تست: {tests["test_ratio"]:.1%}')

    # ۶. وابستگی‌ها
    print('\n  [۶] تحلیل وابستگی‌ها …')
    deps = analyze_dependencies()
    print(f'     📦 npm: {len(deps["npm"])} بسته')
    print(f'     🐍 PyPI: {len(deps["pypi"])} بسته')

    # ۷. پیشنهادهای ارتقا
    print('\n  [۷] پیشنهادهای ارتقا …')
    recs = generate_recommendations(structure, complexity, quality,
                                    security, tests, deps)
    for i, r in enumerate(recs, 1):
        icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵'}
        print(f'\n     {icon.get(r["priority"], "⚪")} [{r["priority"].upper()}] '
              f'{r["title"]}')
        print(f'        دسته: {r["category"]}')
        print(f'        {r["detail"]}')
        if 'files' in r:
            for f in r['files'][:3]:
                print(f'        📄 {f}')

    # ── خروجی JSON ──
    report = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'project': 'econojin.com/apps',
        'structure': {
            'total_files': len(structure['files']),
            'apps': {k: {'files': v['files'], 'lines': v['lines']}
                     for k, v in structure['stats'].items()},
        },
        'complexity': {
            'total_functions': complexity['total_functions'],
            'high_complexity_count': len(complexity['high_complexity']),
            'long_functions_count': len(complexity['long_functions']),
            'top_10': complexity['top_20'][:10],
        },
        'quality': {
            'docstring_ratio': round(doc_r, 3),
            'type_hint_ratio': round(hint_r, 3),
            'logging_ratio': round(log_r, 3),
            'bare_except_count': len(quality['bare_except']),
            'print_count': len(quality['print_statements']),
            'todo_count': len(quality['todo_fixme']),
        },
        'security': {
            'total_issues': security['total'],
            'by_severity': dict(by_sev),
        },
        'tests': {
            'test_files': tests['test_files'],
            'source_files': tests['source_files'],
            'ratio': tests['test_ratio'],
        },
        'dependencies': {
            'npm_count': len(deps['npm']),
            'pypi_count': len(deps['pypi']),
        },
        'recommendations': recs,
    }

    out = ROOT / 'apps-analysis.json'
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'\n{"═" * 60}')
    print(f'  📄 گزارش JSON: {out.name}')
    print(f'  📊 {len(recs)} پیشنهاد ارتقا')
    print(f'{"═" * 60}')
    return 0


if __name__ == '__main__':
    sys.exit(main())