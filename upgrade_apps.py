#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
upgrade_apps.py — ارتقای خودکار کیفیت کد (فاز ۱: logging + type hints)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
۱. افزودن structlog به فایل‌های بدون logging
۲. افزودن type hints به توابع بدون annotation
۳. گزارش پیشرفت
'''
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APPS = ROOT / 'apps'

SKIP = ('node_modules', '__pycache__', 'tests', 'test_', 'conftest',
        '.pnpm-store', 'dist', 'build')


def should_skip(path: Path) -> bool:
    s = str(path).replace('\\', '/')
    return any(skip in s for skip in SKIP)


# ═══════════════════════════════════════════════════════════
#  ۱. افزودن logging
# ═══════════════════════════════════════════════════════════

LOGGING_IMPORT = 'import structlog\n\nlogger = structlog.get_logger(__name__)\n'
LOGGING_IMPORT_STD = 'import logging\n\nlogger = logging.getLogger(__name__)\n'


def add_logging(files: list[Path], apply: bool) -> int:
    count = 0
    for f in files:
        try:
            text = f.read_text(encoding='utf-8')
        except OSError:
            continue
        if 'logging' in text or 'logger' in text or 'structlog' in text:
            continue

        # پیدا کردن اولین import
        lines = text.splitlines(keepends=True)
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                insert_idx = i
                break

        # استفاده از logging استاندارد (ساده‌تر)
        new_lines = lines[:insert_idx] + [LOGGING_IMPORT_STD] + lines[insert_idx:]
        if apply:
            f.write_text(''.join(new_lines), encoding='utf-8')
        count += 1
        rel = f.relative_to(ROOT)
        print(f'  {"✅" if apply else "📄"} {rel}')
    return count


# ═══════════════════════════════════════════════════════════
#  ۲. شناسایی توابع بدون type hints
# ═══════════════════════════════════════════════════════════

def find_missing_hints(files: list[Path]) -> list[dict]:
    missing = []
    for f in files:
        try:
            tree = ast.parse(f.read_text(encoding='utf-8', errors='ignore'))
        except SyntaxError:
            continue
        rel = str(f.relative_to(ROOT))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                has_return = node.returns is not None
                has_args = any(a.annotation for a in node.args.args
                               if a.arg != 'self')
                if not has_return or not has_args:
                    missing.append({
                        'file': rel,
                        'line': node.lineno,
                        'name': node.name,
                        'missing_return': not has_return,
                        'missing_args': not has_args,
                    })
    return missing


# ═══════════════════════════════════════════════════════════
#  ۳. شناسایی فایل‌های بدون logging
# ═══════════════════════════════════════════════════════════

def find_no_logging(files: list[Path]) -> list[Path]:
    result = []
    for f in files:
        try:
            text = f.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        if 'logging' not in text and 'logger' not in text and 'structlog' not in text:
            result.append(f)
    return result


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════

def main() -> int:
    apply = '--apply' in sys.argv
    print('═' * 60)
    print('  🚀 ارتقای کیفیت کد — فاز ۱')
    print('═' * 60)
    if not apply:
        print('  ℹ️  حالت گزارش — برای اعمال: --apply')

    # جمع‌آوری فایل‌های Python
    py_files = [f for f in APPS.rglob('*.py') if not should_skip(f)]
    print(f'\n  📁 {len(py_files)} فایل Python')

    # ── ۱. Logging ──
    print(f'\n  [۱] افزودن logging …')
    no_log = find_no_logging(py_files)
    print(f'     {len(no_log)} فایل بدون logging')
    if no_log:
        added = add_logging(no_log[:20], apply)  # حداکثر ۲۰ فایل
        if len(no_log) > 20:
            print(f'     … و {len(no_log) - 20} فایل دیگر')
    else:
        print('     ✅ همه فایل‌ها logging دارند')

    # ── ۲. Type Hints ──
    print(f'\n  [۲] شناسایی توابع بدون type hints …')
    missing = find_missing_hints(py_files)
    print(f'     {len(missing)} تابع بدون type hints کامل')
    if missing:
        print(f'\n     ۱۰ مورد اول:')
        for m in missing[:10]:
            flags = []
            if m['missing_return']:
                flags.append('return')
            if m['missing_args']:
                flags.append('args')
            print(f'     📄 {m["file"]}:{m["line"]} → {m["name"]}() '
                  f'(بدون: {", ".join(flags)})')

    # ── ۳. خلاصه ──
    print(f'\n{"═" * 60}')
    print(f'  📊 خلاصه:')
    print(f'     logging: {len(no_log)} فایل نیاز دارد')
    print(f'     type hints: {len(missing)} تابع نیاز دارد')
    if apply:
        print(f'\n  ✅ اعمال شد')
    else:
        print(f'\n  → برای اعمال: python upgrade_apps.py --apply')
    print('═' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())