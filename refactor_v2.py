#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
refactor_v2.py — بازسازی امن با مدیریت صحیح indentation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
بلوک‌های try/for/if بزرگ را به توابع helper استخراج می‌کند.
'''
from __future__ import annotations

import ast
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent

TARGETS = [
    ('apps/shared_ai/ai/tools/code_tools.py',
     ['analyze_code', 'find_bugs', '_analyze_complexity']),
    ('apps/shared_ai/ai/tools/data_tools.py',
     ['generate_chart', 'hypothesis_test', 'correlation_analysis']),
    ('apps/shared_ai/ai/fallback/brain.py',
     ['_detect_intent']),
    ('apps/simulation/validation/router.py',
     ['validation']),
]


def extract_block(lines: list[str], start: int, end: int) -> str:
    block = lines[start:end]
    return textwrap.dedent('\n'.join(block))


def find_func(text: str, name: str) -> tuple[int, int, int] | None:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == name:
                return node.lineno - 1, node.end_lineno, node.col_offset
    return None


def find_large_blocks(text: str, func_name: str, min_lines: int = 15) -> list[dict]:
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
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.Try, ast.For, ast.If)):
                end = child.end_lineno or child.lineno
                size = end - child.lineno + 1
                if size >= min_lines:
                    blocks.append({
                        'type': type(child).__name__,
                        'start': child.lineno - 1,
                        'end': end,
                        'size': size,
                        'col': child.col_offset,
                    })
    return blocks


def refactor_one(filepath: Path, func_name: str, apply: bool) -> bool:
    text = filepath.read_text(encoding='utf-8')
    lines = text.splitlines()

    info = find_func(text, func_name)
    if not info:
        print(f'     ⚪ {func_name}() — یافت نشد')
        return False

    func_start, func_end, func_col = info
    blocks = find_large_blocks(text, func_name)

    if not blocks:
        print(f'     ⚪ {func_name}() — بلوک بزرگ یافت نشد')
        return False

    # فقط بزرگ‌ترین بلوک
    block = max(blocks, key=lambda b: b['size'])
    btype = block['type']
    bstart = block['start']
    bend = block['end']
    bsize = block['size']
    bcol = block['col']

    # indent تابع
    indent = ' ' * func_col
    body_indent = ' ' * (func_col + 4)

    # نام helper
    helper_name = f'_{func_name}_extracted'

    # استخراج بلوک
    block_lines = lines[bstart:bend]
    block_text = '\n'.join(block_lines)
    dedented = textwrap.dedent(block_text)

    # ساخت helper function
    helper_lines = [
        f'{indent}def {helper_name}():',
        f'{body_indent}"""Extracted from {func_name}() — {btype} block ({bsize} lines)."""',
    ]
    for hl in dedented.splitlines():
        helper_lines.append(f'{body_indent}{hl}' if hl.strip() else '')
    helper_lines.append('')

    helper_text = '\n'.join(helper_lines)

    # ساخت call line
    call_line = f'{body_indent}{helper_name}()  # refactored: was {btype} block'

    if not apply:
        print(f'     📋 {func_name}():')
        print(f'        {btype} @ line {bstart+1}-{bend} ({bsize} lines)')
        print(f'        → {helper_name}()')
        return True

    # اعمال: جایگزینی بلوک با call
    new_lines = lines[:bstart] + [call_line] + lines[bend:]

    # درج helper قبل از تابع
    new_func_start = find_func('\n'.join(new_lines), func_name)
    if new_func_start:
        insert_at = new_func_start[0]
        helper_insert = helper_text.splitlines()
        new_lines = new_lines[:insert_at] + helper_insert + [''] + new_lines[insert_at:]

    new_text = '\n'.join(new_lines)

    # validate
    try:
        ast.parse(new_text)
    except SyntaxError as e:
        print(f'     ❌ {func_name}() — syntax error: {e}')
        print(f'        → فایل تغییر نکرد')
        return False

    # backup + write
    backup = filepath.with_suffix('.py.bak')
    if not backup.exists():
        backup.write_text(text, encoding='utf-8')
    filepath.write_text(new_text, encoding='utf-8')
    print(f'     ✅ {func_name}() → {helper_name}() ({bsize} lines extracted)')
    return True


def main() -> int:
    apply = '--apply' in sys.argv
    print('═' * 60)
    print('  🚀 فاز ۲ — بازسازی امن (v2)')
    print('═' * 60)
    if not apply:
        print('  ℹ️  حالت تحلیل — برای اعمال: --apply')

    ok = 0
    fail = 0

    for rel, funcs in TARGETS:
        filepath = ROOT / rel
        if not filepath.exists():
            continue
        print(f'\n  📄 {rel}')

        for func_name in funcs:
            success = refactor_one(filepath, func_name, apply)
            if success:
                ok += 1
            else:
                fail += 1

    # syntax check نهایی
    if apply:
        print(f'\n{"─" * 60}')
        print('  🔍 بررسی syntax نهایی …')
        all_ok = True
        for rel, _ in TARGETS:
            fp = ROOT / rel
            if not fp.exists():
                continue
            try:
                ast.parse(fp.read_text(encoding='utf-8'))
                print(f'     ✅ {rel}')
            except SyntaxError as e:
                print(f'     ❌ {rel}: {e}')
                # restore backup
                bak = fp.with_suffix('.py.bak')
                if bak.exists():
                    fp.write_text(bak.read_text(encoding='utf-8'), encoding='utf-8')
                    print(f'     ↩️  بازگردانی از backup')
                all_ok = False

        # حذف backup ها
        if all_ok:
            for rel, _ in TARGETS:
                bak = (ROOT / rel).with_suffix('.py.bak')
                if bak.exists():
                    bak.unlink()

    print(f'\n{"═" * 60}')
    print(f'  📊 نتیجه: {ok} موفق | {fail} ناموفق')
    if apply and ok > 0:
        print(f'\n  📋 commit:')
        print(f'     git add -A')
        print(f'     git commit -m "refactor: phase 2 - extract large blocks"')
        print(f'     git push')
    elif not apply:
        print(f'\n  → python refactor_v2.py --apply')
    print('═' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())