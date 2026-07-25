#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
refactor_dispatch.py — بازسازی if/elif زنجیره‌ای به Dictionary Dispatch
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
هر شاخه if/elif → تابع helper مستقل
تابع اصلی → dispatcher ساده (پیچیدگی ~۳)
'''
from __future__ import annotations

import ast
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent

TARGETS = [
    ('apps/shared_ai/ai/tools/data_tools.py',
     ['_generate_chart_extracted', '_hypothesis_test_extracted',
      '_correlation_analysis_extracted']),
    ('apps/simulation/validation/router.py',
     ['validation']),
]


def get_source(text: str, name: str) -> tuple[str, int, int, int] | None:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    lines = text.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == name:
                src = '\n'.join(lines[node.lineno-1:node.end_lineno])
                return src, node.lineno-1, node.end_lineno, node.col_offset
    return None


def find_if_chain(node: ast.If) -> list[dict]:
    '''باز کردن زنجیره if/elif/else.'''
    branches = []
    current = node
    while isinstance(current, ast.If):
        try:
            cond = ast.unparse(current.test)
        except Exception:
            cond = 'condition'
        branches.append({
            'condition': cond,
            'body_start': current.lineno,
            'body_end': current.body[-1].end_lineno if current.body else current.lineno,
            'body_lines': (current.body[-1].end_lineno - current.body[0].lineno + 1)
                          if current.body else 0,
        })
        if current.orelse and len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
            current = current.orelse[0]
        else:
            if current.orelse:
                branches.append({
                    'condition': 'else',
                    'body_start': current.orelse[0].lineno,
                    'body_end': current.orelse[-1].end_lineno,
                    'body_lines': (current.orelse[-1].end_lineno - current.orelse[0].lineno + 1),
                })
            break
    return branches


def make_safe_name(cond: str) -> str:
    name = re.sub(r'[^a-zA-Z0-9_]', '_', cond[:40]).strip('_').lower()
    name = re.sub(r'_+', '_', name)
    return name or 'default'


def refactor_to_dispatch(filepath: Path, func_name: str, apply: bool) -> bool:
    text = filepath.read_text(encoding='utf-8')
    lines = text.splitlines()

    info = get_source(text, func_name)
    if not info:
        print(f'     ⚪ {func_name}() — یافت نشد')
        return False

    func_src, func_start, func_end, func_col = info

    # پیدا کردن if chain
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return False

    if_node = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == func_name:
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, ast.If):
                        end = child.end_lineno or child.lineno
                        size = end - child.lineno + 1
                        if size > 20:
                            if_node = child
                            break
                break

    if not if_node:
        print(f'     ⚪ {func_name}() — if chain بزرگ یافت نشد')
        return False

    branches = find_if_chain(if_node)
    if len(branches) < 3:
        print(f'     ⚪ {func_name}() — فقط {len(branches)} شاخه (حداقل ۳ لازم)')
        return False

    indent = ' ' * func_col
    body_indent = ' ' * (func_col + 4)

    if not apply:
        print(f'     📋 {func_name}() → {len(branches)} شاخه:')
        for b in branches:
            safe = make_safe_name(b['condition'])
            print(f'        • {b["condition"][:50]} ({b["body_lines"]} lines) '
                  f'→ _{func_name}_{safe}()')
        return True

    # ساخت توابع helper
    helpers = []
    dispatch_entries = []

    for b in branches:
        if b['condition'] == 'else':
            continue
        safe = make_safe_name(b['condition'])
        helper_name = f'_{func_name}_{safe}'

        # استخراج بدنه شاخه
        bstart = b['body_start'] - 1
        bend = b['body_end']
        branch_lines = lines[bstart:bend]
        branch_text = textwrap.dedent('\n'.join(branch_lines))

        # ساخت helper
        helper = f'{indent}def {helper_name}(data, **kwargs):\n'
        helper += f'{body_indent}"""Handler: {b["condition"][:60]}"""\n'
        for hl in branch_text.splitlines():
            helper += f'{body_indent}{hl}\n' if hl.strip() else '\n'
        helper += '\n'
        helpers.append(helper)

        # dispatch entry
        key = b['condition'].strip()
        # سعی در استخراج مقدار رشته‌ای
        str_match = re.search(r"==\s*['\"]([^'\"]+)['\"]", key)
        if str_match:
            dispatch_entries.append(f"        '{str_match.group(1)}': {helper_name},")
        else:
            dispatch_entries.append(f"        # {key[:50]}: {helper_name},")

    if not helpers:
        print(f'     ⚪ {func_name}() — شاخه قابل استخراج یافت نشد')
        return False

    # ساخت dispatcher
    dispatcher = f'{indent}_DISPATCH_{func_name.upper()} = {{\n'
    dispatcher += '\n'.join(dispatch_entries)
    dispatcher += f'\n{indent}}}\n\n'

    # نمایش
    print(f'     ✅ {func_name}() → {len(helpers)} handler + dispatcher')
    for h in helpers:
        name = h.split('(')[0].replace(f'{indent}def ', '')
        print(f'        • {name}()')

    # نوشتن: helpers + dispatcher قبل از تابع
    insert_text = '\n'.join(helpers) + '\n' + dispatcher
    new_lines = lines[:func_start] + insert_text.splitlines() + [''] + lines[func_start:]
    new_text = '\n'.join(new_lines)

    # validate
    try:
        ast.parse(new_text)
    except SyntaxError as e:
        print(f'     ❌ {func_name}() — syntax error: {e}')
        return False

    filepath.write_text(new_text, encoding='utf-8')
    return True


def main() -> int:
    apply = '--apply' in sys.argv
    print('═' * 60)
    print('  🚀 Dictionary Dispatch Refactoring')
    print('═' * 60)
    if not apply:
        print('  ℹ️  حالت تحلیل — برای اعمال: --apply')

    ok = 0
    for rel, funcs in TARGETS:
        fp = ROOT / rel
        if not fp.exists():
            continue
        print(f'\n  📄 {rel}')
        for func_name in funcs:
            if refactor_to_dispatch(fp, func_name, apply):
                ok += 1

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
    print(f'  📊 {ok} تابع پردازش شد')
    if apply and ok > 0:
        print(f'\n  📋 commit:')
        print(f'     git add -A')
        print(f'     git commit -m "refactor: phase 2c - dictionary dispatch pattern"')
        print(f'     git push')
    elif not apply:
        print(f'\n  → python refactor_dispatch.py --apply')
    print('═' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())