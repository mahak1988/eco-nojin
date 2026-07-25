#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
upgrade_phase1b.py — تکمیل فاز ۱: logging کامل + type hints اولیه
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
۱. افزودن logging به همه ۱۹۱ فایل باقی‌مانده
۲. افزودن return type (-> None) به توابع بدون آن
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

LOGGING_BLOCK = 'import logging\n\nlogger = logging.getLogger(__name__)\n'


def should_skip(path: Path) -> bool:
    s = str(path).replace('\\', '/')
    return any(skip in s for skip in SKIP)


def add_logging_all(apply: bool) -> tuple[int, int]:
    added = 0
    skipped = 0
    for f in APPS.rglob('*.py'):
        if should_skip(f):
            continue
        try:
            text = f.read_text(encoding='utf-8')
        except OSError:
            continue

        # skip فایل‌های خیلی کوچک (<۵ خط کد واقعی)
        code_lines = [l for l in text.splitlines()
                      if l.strip() and not l.strip().startswith('#')]
        if len(code_lines) < 5:
            skipped += 1
            continue

        if 'logging' in text or 'logger' in text or 'structlog' in text:
            skipped += 1
            continue

        # پیدا کردن اولین import
        lines = text.splitlines(keepends=True)
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                insert_idx = i
                break

        new_lines = lines[:insert_idx] + [LOGGING_BLOCK] + lines[insert_idx:]

        if apply:
            f.write_text(''.join(new_lines), encoding='utf-8')
        added += 1

    return added, skipped


def add_return_types(apply: bool) -> int:
    count = 0
    for f in APPS.rglob('*.py'):
        if should_skip(f):
            continue
        try:
            text = f.read_text(encoding='utf-8')
            tree = ast.parse(text)
        except (SyntaxError, OSError):
            continue

        lines = text.splitlines(keepends=True)
        modified = False

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.returns is not None:
                    continue
                # پیدا کردن خط def
                line_idx = node.lineno - 1
                if line_idx >= len(lines):
                    continue
                line = lines[line_idx]
                # بررسی اینکه خط شامل ): یا ) -> است
                if re.search(r'\)\s*:', line):
                    # افزودن -> None قبل از :
                    new_line = re.sub(r'\)(\s*):', r') -> None\1:', line)
                    if new_line != line:
                        lines[line_idx] = new_line
                        modified = True
                        count += 1

        if modified and apply:
            # validate
            try:
                ast.parse(''.join(lines))
                f.write_text(''.join(lines), encoding='utf-8')
            except SyntaxError:
                pass  # revert

    return count


def main() -> int:
    apply = '--apply' in sys.argv
    print('═' * 60)
    print('  🚀 تکمیل فاز ۱ — logging + type hints')
    print('═' * 60)
    if not apply:
        print('  ℹ️  حالت گزارش — برای اعمال: --apply')

    # ۱. Logging
    print('\n  [۱] افزودن logging به همه فایل‌ها …')
    added, skipped = add_logging_all(apply)
    print(f'     ✅ {added} فایل اصلاح شد')
    print(f'     ⚪ {skipped} فایل skip شد (کوچک یا已有 logging)')

    # ۲. Return types
    print('\n  [۲] افزودن -> None به توابع …')
    rt_count = add_return_types(apply)
    print(f'     ✅ {rt_count} تابع اصلاح شد')

    # ۳. خلاصه
    print(f'\n{"═" * 60}')
    if apply:
        print(f'  ✅ اعمال شد: {added} logging + {rt_count} return types')
        print(f'\n  📋 commit:')
        print(f'     git add -A')
        print(f'     git commit -m "quality: complete logging + return types (phase 1b)"')
        print(f'     git push')
    else:
        print(f'  → {added} logging + {rt_count} return types آماده اعمال')
        print(f'  → python upgrade_phase1b.py --apply')
    print('═' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())