#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
refactor_phase2.py — بازسازی توابع پیچیده + افزودن ویژگی‌های جدید
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
مرحله ۱: تحلیل و نمایش ساختار توابع پیچیده
مرحله ۲: شکستن به توابع کوچک (Pipeline/Strategy)
مرحله ۳: افزودن قابلیت‌های جدید
'''
from __future__ import annotations

import ast
import re
import shutil
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ── فایل‌های هدف ──
TARGETS = [
    {
        'file': 'apps/shared_ai/ai/tools/code_tools.py',
        'functions': ['analyze_code', 'find_bugs', '_analyze_complexity'],
    },
    {
        'file': 'apps/shared_ai/ai/tools/data_tools.py',
        'functions': ['generate_chart', 'hypothesis_test', 'correlation_analysis'],
    },
    {
        'file': 'apps/shared_ai/ai/fallback/brain.py',
        'functions': ['_detect_intent'],
    },
    {
        'file': 'apps/simulation/validation/router.py',
        'functions': ['validation'],
    },
]


# ═══════════════════════════════════════════════════════════
#  ۱. تحلیل ساختار تابع
# ═══════════════════════════════════════════════════════════

def analyze_function(filepath: Path, func_name: str) -> dict | None:
    try:
        text = filepath.read_text(encoding='utf-8')
        tree = ast.parse(text)
    except (SyntaxError, OSError):
        return None

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name != func_name:
                continue

            lines = text.splitlines()
            func_lines = lines[node.lineno - 1:node.end_lineno]
            func_text = '\n'.join(func_lines)

            # شمارش بلوک‌ها
            blocks = {'if': 0, 'for': 0, 'while': 0, 'try': 0,
                      'with': 0, 'return': 0, 'assign': 0}
            for child in ast.walk(node):
                if isinstance(child, ast.If): blocks['if'] += 1
                elif isinstance(child, ast.For): blocks['for'] += 1
                elif isinstance(child, ast.While): blocks['while'] += 1
                elif isinstance(child, ast.Try): blocks['try'] += 1
                elif isinstance(child, ast.With): blocks['with'] += 1
                elif isinstance(child, ast.Return): blocks['return'] += 1
                elif isinstance(child, ast.Assign): blocks['assign'] += 1

            # پیچیدگی
            complexity = 1
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.While, ast.For,
                                      ast.ExceptHandler, ast.comprehension)):
                    complexity += 1
                elif isinstance(child, ast.BoolOp):
                    complexity += len(child.values) - 1

            # شناسایی بلوک‌های قابل استخراج
            extractable = []
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.If):
                    extractable.append({
                        'type': 'if-block',
                        'line': child.lineno,
                        'lines': (child.end_lineno or child.lineno) - child.lineno + 1,
                    })
                elif isinstance(child, ast.For):
                    extractable.append({
                        'type': 'for-block',
                        'line': child.lineno,
                        'lines': (child.end_lineno or child.lineno) - child.lineno + 1,
                    })
                elif isinstance(child, ast.Try):
                    extractable.append({
                        'type': 'try-block',
                        'line': child.lineno,
                        'lines': (child.end_lineno or child.lineno) - child.lineno + 1,
                    })
                elif isinstance(child, ast.Assign):
                    extractable.append({
                        'type': 'assign',
                        'line': child.lineno,
                        'lines': 1,
                    })

            return {
                'name': func_name,
                'file': str(filepath.relative_to(ROOT)),
                'line': node.lineno,
                'total_lines': len(func_lines),
                'complexity': complexity,
                'args': [a.arg for a in node.args.args],
                'has_docstring': bool(ast.get_docstring(node)),
                'has_return_type': node.returns is not None,
                'blocks': blocks,
                'extractable': extractable,
                'source': func_text,
            }
    return None


# ═══════════════════════════════════════════════════════════
#  ۲. تولید Refactor Plan
# ═══════════════════════════════════════════════════════════

def generate_plan(info: dict) -> dict:
    name = info['name']
    complexity = info['complexity']
    blocks = info['blocks']
    extractable = info['extractable']

    # شناسایی بلوک‌های بزرگ قابل استخراج
    large_blocks = [b for b in extractable if b['lines'] > 10]

    # پیشنهاد الگوی بازسازی
    if blocks['if'] > 5:
        pattern = 'Strategy Pattern'
        reason = f"{blocks['if']} شاخه شرطی — هر شاخه یک Strategy جداگانه"
    elif blocks['for'] > 3:
        pattern = 'Pipeline Pattern'
        reason = f"{blocks['for']} حلقه — هر مرحله یک Pipeline stage"
    elif blocks['try'] > 2:
        pattern = 'Template Method'
        reason = f"{blocks['try']} بلوک try — قالب مشترک + پیاده‌سازی خاص"
    else:
        pattern = 'Extract Method'
        reason = 'شکستن به توابع کوچک‌تر بر اساس مسئولیت'

    # پیشنهاد نام توابع جدید
    sub_functions = []
    for i, block in enumerate(large_blocks[:5], 1):
        sub_name = f'_{name}_step{i}'
        sub_functions.append({
            'name': sub_name,
            'type': block['type'],
            'line': block['line'],
            'lines': block['lines'],
        })

    return {
        'function': name,
        'pattern': pattern,
        'reason': reason,
        'complexity_before': complexity,
        'complexity_target': '<10',
        'sub_functions': sub_functions,
        'large_blocks': len(large_blocks),
    }


# ═══════════════════════════════════════════════════════════
#  ۳. بازسازی خودکار (Extract Method)
# ═══════════════════════════════════════════════════════════

def refactor_function(filepath: Path, func_name: str, dry_run: bool = True) -> bool:
    try:
        text = filepath.read_text(encoding='utf-8')
        tree = ast.parse(text)
    except (SyntaxError, OSError):
        return False

    lines = text.splitlines(keepends=True)

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != func_name:
            continue

        # شناسایی بلوک‌های قابل استخراج
        extractable = []
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.Try)):
                block_lines = (child.end_lineno or child.lineno) - child.lineno + 1
                if block_lines > 15:
                    extractable.append(child)

        if not extractable:
            print(f'     ⚪ {func_name}() — بلوک قابل استخراج یافت نشد')
            return False

        # تعیین indent
        indent = ' ' * node.col_offset
        body_indent = ' ' * (node.col_offset + 4)

        # ساخت توابع helper
        helpers = []
        calls = []
        for i, block in enumerate(extractable[:4], 1):
            helper_name = f'_{func_name}_part{i}'
            start = block.lineno - 1
            end = block.end_lineno or block.lineno
            block_text = ''.join(lines[start:end])

            # ساخت helper function
            helper = f'\n{indent}def {helper_name}():\n'
            helper += f'{body_indent}"""Extracted from {func_name}() — part {i}."""\n'
            # re-indent block
            for bline in block_text.splitlines(keepends=True):
                helper += f'    {bline}'
            helper += f'\n{body_indent}return None  # TODO: adjust return\n'
            helpers.append(helper)

            # جایگزینی بلوک با call
            call_line = f'{body_indent}{helper_name}()  # refactored\n'
            calls.append((start, end, call_line))

        if dry_run:
            print(f'     📋 {func_name}() → {len(extractable)} بلوک قابل استخراج:')
            for i, block in enumerate(extractable[:4], 1):
                bl = (block.end_lineno or block.lineno) - block.lineno + 1
                tp = type(block).__name__
                print(f'        Part {i}: {tp} @ line {block.lineno} ({bl} lines)')
            return True

        # اعمال: جایگزینی بلوک‌ها (از آخر به اول)
        for start, end, call_line in sorted(calls, reverse=True):
            lines[start:end] = [call_line]

        # افزودن helpers قبل از تابع اصلی
        func_start = node.lineno - 1
        helper_text = ''.join(helpers)
        lines.insert(func_start, helper_text + '\n')

        # validate
        new_text = ''.join(lines)
        try:
            ast.parse(new_text)
        except SyntaxError as e:
            print(f'     ❌ {func_name}() — خطای syntax پس از بازسازی: {e}')
            return False

        # backup + write
        backup = filepath.with_suffix('.py.bak')
        shutil.copy2(filepath, backup)
        filepath.write_text(new_text, encoding='utf-8')
        print(f'     ✅ {func_name}() → {len(calls)} تابع استخراج شد')
        print(f'        backup: {backup.name}')
        return True

    return False


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════

def main() -> int:
    apply = '--apply' in sys.argv
    print('═' * 60)
    print('  🚀 فاز ۲ — بازسازی توابع پیچیده')
    print('═' * 60)
    if not apply:
        print('  ℹ️  حالت تحلیل — برای اعمال: --apply')

    all_plans = []

    for target in TARGETS:
        filepath = ROOT / target['file']
        if not filepath.exists():
            print(f'\n  ⚪ {target["file"]} — یافت نشد')
            continue

        print(f'\n  📄 {target["file"]}')
        print(f'  {"─" * 50}')

        for func_name in target['functions']:
            info = analyze_function(filepath, func_name)
            if not info:
                print(f'     ⚪ {func_name}() — یافت نشد')
                continue

            # نمایش اطلاعات
            print(f'\n     🔍 {func_name}()')
            print(f'        خط: {info["line"]} | طول: {info["total_lines"]} | '
                  f'پیچیدگی: {info["complexity"]}')
            print(f'        آرگومان‌ها: {", ".join(info["args"])}')
            print(f'        بلوک‌ها: if={info["blocks"]["if"]} '
                  f'for={info["blocks"]["for"]} '
                  f'try={info["blocks"]["try"]} '
                  f'return={info["blocks"]["return"]}')

            # refactor plan
            plan = generate_plan(info)
            all_plans.append(plan)
            print(f'        📐 الگو: {plan["pattern"]}')
            print(f'        📝 {plan["reason"]}')
            if plan['sub_functions']:
                print(f'        🔧 توابع پیشنهادی:')
                for sf in plan['sub_functions']:
                    print(f'           • {sf["name"]}() '
                          f'[{sf["type"]} @ line {sf["line"]}, {sf["lines"]} lines]')

            # بازسازی
            if apply:
                refactor_function(filepath, func_name, dry_run=False)
            else:
                refactor_function(filepath, func_name, dry_run=True)

    # خلاصه
    print(f'\n{"═" * 60}')
    print(f'  📊 خلاصه:')
    print(f'     توابع تحلیل‌شده: {len(all_plans)}')
    for p in all_plans:
        print(f'     • {p["function"]}(): {p["complexity_before"]} → {p["complexity_target"]} '
              f'({p["pattern"]})')

    if apply:
        print(f'\n  📋 commit:')
        print(f'     git add -A')
        print(f'     git commit -m "refactor: phase 2 - reduce complexity (Pipeline/Strategy)"')
        print(f'     git push')
    else:
        print(f'\n  → برای اعمال: python refactor_phase2.py --apply')
    print('═' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())