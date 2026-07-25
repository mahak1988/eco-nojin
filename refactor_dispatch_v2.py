#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
refactor_dispatch_v2.py — Dictionary Dispatch (اصلاح‌شده)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if/elif های داخل try/for را هم پیدا می‌کند (ast.walk).
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


def find_if_chains_deep(text: str, func_name: str, min_branches: int = 3,
                        min_size: int = 10) -> list[dict]:
    '''پیدا کردن if/elif chain در هر سطحی (داخل try/for/with).'''
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    chains = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != func_name:
            continue
        # جستجوی عمیق — نه فقط سطح اول
        for child in ast.walk(node):
            if not isinstance(child, ast.If):
                continue
            # باز کردن زنجیره if/elif
            branches = []
            current = child
            while isinstance(current, ast.If):
                try:
                    cond = ast.unparse(current.test)
                except Exception:
                    cond = '...'
                body_end = current.body[-1].end_lineno if current.body else current.lineno
                branches.append({
                    'condition': cond,
                    'start': current.lineno,
                    'end': body_end,
                    'size': body_end - current.lineno + 1,
                })
                if (current.orelse and len(current.orelse) == 1
                        and isinstance(current.orelse[0], ast.If)):
                    current = current.orelse[0]
                else:
                    if current.orelse:
                        branches.append({
                            'condition': 'else',
                            'start': current.orelse[0].lineno,
                            'end': current.orelse[-1].end_lineno,
                            'size': (current.orelse[-1].end_lineno
                                     - current.orelse[0].lineno + 1),
                        })
                    break

            total_size = sum(b['size'] for b in branches)
            if len(branches) >= min_branches and total_size >= min_size:
                chains.append({
                    'branches': branches,
                    'total_size': total_size,
                    'start': child.lineno,
                    'end': branches[-1]['end'],
                })
    # حذف زنجیره‌های تودرتو (فقط بزرگ‌ترین)
    chains.sort(key=lambda c: c['total_size'], reverse=True)
    return chains[:1]  # فقط بزرگ‌ترین


def make_name(cond: str) -> str:
    n = re.sub(r'[^a-zA-Z0-9_]', '_', cond[:35]).strip('_').lower()
    return re.sub(r'_+', '_', n) or 'default'


def refactor(filepath: Path, func_name: str, apply: bool) -> bool:
    text = filepath.read_text(encoding='utf-8')
    lines = text.splitlines()

    chains = find_if_chains_deep(text, func_name)
    if not chains:
        print(f'     ⚪ {func_name}() — if chain یافت نشد')
        return False

    chain = chains[0]
    branches = chain['branches']

    # پیدا کردن indent تابع
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return False
    func_col = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == func_name:
                func_col = node.col_offset
                break

    indent = ' ' * func_col
    body_indent = ' ' * (func_col + 4)

    if not apply:
        print(f'     📋 {func_name}() → {len(branches)} شاخه '
              f'({chain["total_size"]} lines):')
        for b in branches:
            safe = make_name(b['condition'])
            print(f'        • {b["condition"][:50]} ({b["size"]} lines) '
                  f'→ _{func_name}_{safe}()')
        return True

    # ساخت handlers
    handlers = []
    dispatch = []

    for b in branches:
        if b['condition'] == 'else':
            continue
        safe = make_name(b['condition'])
        hname = f'_{func_name}_{safe}'

        bstart = b['start'] - 1
        bend = b['end']
        blines = lines[bstart:bend]
        dedented = textwrap.dedent('\n'.join(blines))

        h = f'{indent}def {hname}(data, **kw):\n'
        h += f'{body_indent}"""Handler: {b["condition"][:55]}"""\n'
        for hl in dedented.splitlines():
            h += f'{body_indent}{hl}\n' if hl.strip() else '\n'
        h += '\n'
        handlers.append(h)

        sm = re.search(r"==\s*['\"]([^'\"]+)['\"]", b['condition'])
        if sm:
            dispatch.append(f"{body_indent}'{sm.group(1)}': {hname},")
        else:
            dispatch.append(f"{body_indent}# {b['condition'][:45]}: {hname},")

    if not handlers:
        print(f'     ⚪ {func_name}() — handler قابل ساخت نیست')
        return False

    # dispatcher table
    table = f'{indent}_HANDLERS_{func_name.upper()} = {{\n'
    table += '\n'.join(dispatch)
    table += f'\n{indent}}}\n\n'

    # درج قبل از تابع
    func_line = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == func_name:
                func_line = node.lineno - 1
                break

    if func_line is None:
        return False

    insert = '\n'.join(handlers) + '\n' + table
    new_lines = (lines[:func_line]
                 + insert.splitlines() + ['']
                 + lines[func_line:])
    new_text = '\n'.join(new_lines)

    try:
        ast.parse(new_text)
    except SyntaxError as e:
        print(f'     ❌ {func_name}() — syntax: {e}')
        return False

    filepath.write_text(new_text, encoding='utf-8')
    print(f'     ✅ {func_name}() → {len(handlers)} handler + dispatch table')
    return True


def main() -> int:
    apply = '--apply' in sys.argv
    print('═' * 60)
    print('  🚀 Dictionary Dispatch v2 (deep search)')
    print('═' * 60)
    if not apply:
        print('  ℹ️  حالت تحلیل — برای اعمال: --apply')

    ok = 0
    for rel, funcs in TARGETS:
        fp = ROOT / rel
        if not fp.exists():
            continue
        print(f'\n  📄 {rel}')
        for fn in funcs:
            if refactor(fp, fn, apply):
                ok += 1

    if apply:
        print(f'\n{"─" * 60}')
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
    print(f'  📊 {ok} تابع')
    if apply and ok:
        print(f'\n     git add -A')
        print(f'     git commit -m "refactor: phase 2c - dispatch pattern"')
        print(f'     git push')
    elif not apply:
        print(f'\n  → python refactor_dispatch_v2.py --apply')
    print('═' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())