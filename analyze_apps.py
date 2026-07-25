#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''quick_audit.py — اسکن سریع کیفیت apps/'''
from __future__ import annotations
import ast, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APPS = ROOT / 'apps'
SKIP = ('node_modules','__pycache__','tests','test_','conftest','.pnpm-store','dist','build','locales_old_backup')

def sk(p):
    s = str(p).replace('\\','/')
    return any(x in s for x in SKIP)

def main():
    files = [f for f in APPS.rglob('*.py') if not sk(f)]
    total = log_c = doc_c = hint_c = 0
    complex_funcs = []
    long_funcs = []
    todo_c = 0

    for f in files:
        try:
            text = f.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(text)
        except (SyntaxError, OSError):
            continue
        code = [l for l in text.splitlines() if l.strip() and not l.strip().startswith('#')]
        if len(code) < 3:
            continue
        total += 1
        rel = str(f.relative_to(ROOT))

        if 'logging' in text or 'logger' in text or 'structlog' in text:
            log_c += 1
        if ast.get_docstring(tree):
            doc_c += 1
        has_h = False
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if n.returns or any(a.annotation for a in n.args.args if a.arg != 'self'):
                    has_h = True
                # complexity
                c = 1
                for ch in ast.walk(n):
                    if isinstance(ch, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                       ast.ExceptHandler, ast.With, ast.Assert, ast.comprehension)):
                        c += 1
                    elif isinstance(ch, ast.BoolOp):
                        c += len(ch.values) - 1
                lines = (n.end_lineno or n.lineno) - n.lineno + 1
                if c > 15:
                    complex_funcs.append((c, lines, rel, n.lineno, n.name))
                if lines > 50:
                    long_funcs.append((lines, rel, n.lineno, n.name))
        if has_h:
            hint_c += 1
        todo_c += len(re.findall(r'\b(TODO|FIXME|HACK|XXX)\b', text, re.I))

    # tests
    test_f = len([f for f in APPS.rglob('*.py') if not sk(f) and ('test' in f.name.lower() or '/tests/' in str(f).replace('\\','/'))])
    src_f = total

    print('=' * 60)
    print('  Quick Audit — apps/')
    print('=' * 60)
    print(f'\n  Files: {total}')
    print(f'\n  logging:    {log_c}/{total} = {round(log_c/max(total,1)*100)}%')
    print(f'  docstring:  {doc_c}/{total} = {round(doc_c/max(total,1)*100)}%')
    print(f'  type hints: {hint_c}/{total} = {round(hint_c/max(total,1)*100)}%')
    print(f'  tests:      {test_f}/{src_f} = {round(test_f/max(src_f,1)*100)}%')
    print(f'  TODO/FIXME: {todo_c}')
    print(f'\n  Complex (>15): {len(complex_funcs)}')
    for c, l, f, ln, n in sorted(complex_funcs, reverse=True)[:10]:
        print(f'    {c:>3} | {l:>4} lines | {f}:{ln} -> {n}()')
    print(f'\n  Long (>50 lines): {len(long_funcs)}')

    # JSON
    report = {
        'logging': round(log_c/max(total,1)*100),
        'docstring': round(doc_c/max(total,1)*100),
        'type_hints': round(hint_c/max(total,1)*100),
        'test_ratio': round(test_f/max(src_f,1)*100),
        'todo': todo_c,
        'complex_funcs': len(complex_funcs),
        'long_funcs': len(long_funcs),
    }
    (ROOT / 'quick-audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'\n  Report: quick-audit.json')
    print('=' * 60)

if __name__ == '__main__':
    main()