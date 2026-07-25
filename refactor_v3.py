#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
refactor_v3.py — دور دوم بازسازی: استخراج if/elif blocks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
توابع استخراج‌شده فاز ۲ هنوز پیچیدگی بالا دارند.
این اسکریپت بلوک‌های if/elif بزرگ را به توابع helper تقسیم می‌کند.
'''
from __future__ import annotations

import ast
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# توابع هدف (استخراج‌شده فاز ۲ + validation)
TARGETS = [
    ('apps/shared_ai/ai/tools/code_tools.py',
     ['_analyze_code_extracted', '_find_bugs_extracted', '__analyze_complexity_extracted']),
    ('apps/shared_ai/ai/tools/data_tools.py',
     ['_generate_chart_extracted', '_hypothesis_test_extracted', '_correlation_analysis_extracted']),
    ('apps/shared_ai/ai/fallback/brain.py',
     ['__detect_intent_extracted']),
    ('apps/simulation/validation/router.py',
     ['validation']),
]


def find_func_range(text: str, name: str) -> tuple[int, int, int] | None:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == name:
                return node.lineno - 1, node.end_lineno, node.col_offset
    return None


def find_if_blocks(text: str, func_name: str, min_lines: int = 8) -> list[dict]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    blocks = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != func_name:
            continue
        # فقط بلوک‌های if سطح اول بدنه تابع
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.If):
                end = child.end_lineno or child.lineno
                size = end - child.lineno + 1
                if size >= min_lines:
                    # شناسایی شرط
                    try:
                        cond = ast.unparse(child.test)[:60]
                    except Exception:
                        cond = '...'
                    blocks.append({
                        'start': child.lineno - 1,
                        'end': end,
                        'size': size,
                        'condition': cond,
                    })
    return blocks


def refactor_if_blocks(filepath: Path, func_name: str, apply: bool) -> int:
    text = filepath.read_text(encoding='utf-8')
    lines = text.splitlines()

    info = find_func_range(text, func_name)
    if not info:
        return 0

    func_start, func_end, func_col = info
    blocks = find_if_blocks(text, func_name)

    if not blocks:
        return 0

    indent = ' ' * func_col
    body_indent = ' ' * (func_col + 4)
    extracted = 0

    # پردازش از آخر به اول (برای حفظ ایندکس)
    for i, block in enumerate(sorted(blocks, key=lambda b: b['start'], reverse=True)):
        bstart = block['start']
        bend = block['end']
        bsize = block['size']
        cond = block['condition']

        # نام helper بر اساس شرط
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', cond[:30]).strip('_').lower()
        helper_name = f'_{func_name}_{safe_name or f"block{i+1}"}'

        # استخراج بلوک
        block_lines = lines[bstart:bend]
        block_text = '\n'.join(block_lines)
        dedented = textwrap.dedent(block_text)

        # ساخت helper
        helper = [
            f'{indent}def {helper_name}():',
            f'{body_indent}"""Extracted: if {cond[:50]}"""',
        ]
        for hl in dedented.splitlines():
            helper.append(f'{body_indent}{hl}' if hl.strip() else '')
        helper.append('')

        # call line
        call = f'{body_indent}{helper_name}()  # was: if {cond[:40]}'

        if not apply:
            print(f'        📋 if @ line {bstart+1} ({bsize} lines) → {helper_name}()')
            print(f'           شرط: {cond[:60]}')
            extracted += 1
            continue

        # جایگزینی
        lines[bstart:bend] = [call]

        # درج helper قبل از تابع
        func_info = find_func_range('\n'.join(lines), func_name)
        if func_info:
            insert_at = func_info[0]
            lines = lines[:insert_at] + helper + [''] + lines[insert_at:]

        extracted += 1

    if apply and extracted > 0:
        new_text = '\n'.join(lines)
        try:
            ast.parse(new_text)
        except SyntaxError as e:
            print(f'     ❌ {func_name}() — syntax error: {e}')
            return 0
        filepath.write_text(new_text, encoding='utf-8')
        print(f'     ✅ {func_name}() → {extracted} if-block استخراج شد')

    return extracted


def main() -> int:
    apply = '--apply' in sys.argv
    print('═' * 60)
    print('  🚀 فاز ۲ — دور دوم: استخراج if/elif blocks')
    print('═' * 60)
    if not apply:
        print('  ℹ️  حالت تحلیل — برای اعمال: --apply')

    total = 0
    for rel, funcs in TARGETS:
        fp = ROOT / rel
        if not fp.exists():
            continue
        print(f'\n  📄 {rel}')
        for func_name in funcs:
            n = refactor_if_blocks(fp, func_name, apply)
            total += n

    # syntax check
    if apply:
        print(f'\n{"─" * 60}')
        print('  🔍 بررسی syntax …')
        for rel, _ in TARGETS:
            fp = ROOT / rel
            if not fp.exists():
                continue
            try:
                ast.parse(fp.read_text(encoding='utf-8'))
                print(f'     ✅ {rel}')
            except SyntaxError as e:
                print(f'     ❌ {rel}: {e}')

    print(f'\n{"═" * 60}')
    print(f'  📊 {total} بلوک if استخراج شد')
    if apply and total > 0:
        print(f'\n  📋 commit:')
        print(f'     git add -A')
        print(f'     git commit -m "refactor: phase 2b - extract if/elif blocks"')
        print(f'     git push')
    elif not apply:
        print(f'\n  → python refactor_v3.py --apply')
    print('═' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())