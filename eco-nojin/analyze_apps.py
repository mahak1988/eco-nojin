#!/usr/bin/env python3
"""Analyze Econojin apps for complexity metrics."""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any, List, Tuple

ROOT = Path(__file__).resolve().parent
APPS = ROOT / 'apps'
SKIP = ('node_modules','__pycache__','tests','test_','conftest','.pnpm-store','dist','build','locales_old_backup')

def should_skip(path: Path) -> bool:
    """Determine if a path should be skipped during analysis."""
    path_str = str(path).replace('\\','/')
    return any(skip_item in path_str for skip_item in SKIP)

def calculate_complexity(node: ast.AST) -> int:
    """Calculate the complexity score for a function."""
    complexity = 1
    
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                             ast.ExceptHandler, ast.With, ast.Assert)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
            
    return complexity

def analyze_file(file_path: Path) -> Tuple[int, int, int, int, List[Tuple[int, int, str, int, str]], int]:
    """Analyze a single Python file and return metrics."""
    try:
        text = file_path.read_text(encoding='utf-8', errors='ignore')
        tree = ast.parse(text)
    except (SyntaxError, OSError):
        return (0, 0, 0, 0, [], 0)
    
    # Count non-empty, non-comment lines
    code_lines = [line for line in text.splitlines() 
                 if line.strip() and not line.strip().startswith('#')]
    
    if len(code_lines) < 3:
        return (0, 0, 0, 0, [], 0)
    
    has_logging = int('logging' in text or 'logger' in text or 'structlog' in text)
    has_docstring = int(ast.get_docstring(tree) is not None)
    
    # Analyze functions for complexity and length
    has_type_hints = False
    complex_functions = []
    long_functions = []
    todo_count = 0
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check for type hints
            if node.returns or any(a.annotation for a in node.args.args if a.arg != 'self'):
                has_type_hints = True
                
            # Calculate complexity
            complexity = calculate_complexity(node)
            
            # Calculate line count
            end_lineno = getattr(node, 'end_lineno', node.lineno)
            line_count = end_lineno - node.lineno + 1
            
            # Record complex and long functions
            if complexity > 15:
                complex_functions.append((complexity, line_count, file_path.name, node.lineno, node.name))
                
            if line_count > 50:
                long_functions.append((line_count, file_path.name, node.lineno, node.name))
    
    # Find TODO/FIXME comments
    todo_count += len(re.findall(r'\b(TODO|FIXME|HACK|XXX)\b', text, re.I))
    
    return (1, has_logging, has_docstring, 
            int(has_type_hints), complex_functions, long_functions, todo_count)

def main():
    """Main function to analyze Python files in the apps directory."""
    files_to_analyze = [f for f in APPS.rglob('*.py') if not should_skip(f)]
    
    # Metrics counters
    total_files = 0
    logging_count = 0
    docstring_count = 0
    type_hints_count = 0
    complex_functions = []
    long_functions = []
    todo_total = 0
    
    # Analyze each file
    for file_path in files_to_analyze:
        file_metrics = analyze_file(file_path)
        file_count, logging_flag, docstring_flag, type_hints_flag, complex_funcs, long_funcs, todo_count = file_metrics
        
        total_files += file_count
        logging_count += logging_flag
        docstring_count += docstring_flag
        type_hints_count += type_hints_flag
        complex_functions.extend(complex_funcs)
        long_functions.extend(long_funcs)
        todo_total += todo_count
    
    # Count test files
    test_files = len([f for f in APPS.rglob('*.py') if not should_skip(f) and 
                     ('test' in f.name.lower() or '/tests/' in str(f).replace('\\','/'))])
    
    # Print report
    print('=' * 60)
    print('  Code Quality Audit — apps/')
    print('=' * 60)
    print(f'\n  Files analyzed: {total_files}')
    print(f'\n  Logging usage:    {logging_count}/{total_files} = {round(logging_count/max(total_files,1)*100)}%')
    print(f'  Docstrings:       {docstring_count}/{total_files} = {round(docstring_count/max(total_files,1)*100)}%')
    print(f'  Type hints:       {type_hints_count}/{total_files} = {round(type_hints_count/max(total_files,1)*100)}%')
    print(f'  Test coverage:    {test_files}/{total_files} = {round(test_files/max(total_files,1)*100)}%')
    print(f'  TODO/FIXME count: {todo_total}')
    
    # Complex functions report
    print(f'\n  Complex functions (>15 complexity): {len(complex_functions)}')
    for complexity, _, file_name, line_num, func_name in sorted(complex_functions, reverse=True)[:10]:
        print(f'    {complexity:>3} | {file_name}:{line_num} -> {func_name}()')
    
    # Long functions report
    print(f'\n  Long functions (>50 lines): {len(long_functions)}')
    for line_count, file_name, line_num, func_name in sorted(long_functions, key=lambda x: x[0], reverse=True)[:10]:
        print(f'    {line_count:>3} | {file_name}:{line_num} -> {func_name}()')
    
    # Generate JSON report
    report = {
        'logging_usage': round(logging_count/max(total_files,1)*100),
        'docstrings': round(docstring_count/max(total_files,1)*100),
        'type_hints': round(type_hints_count/max(total_files,1)*100),
        'test_coverage': round(test_files/max(total_files,1)*100),
        'todo_count': todo_total,
        'complex_functions': len(complex_functions),
        'long_functions': len(long_functions),
    }
    
    (ROOT / 'quick-audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('\n  Report saved to: quick-audit.json')
    print('=' * 60)

if __name__ == '__main__':
    main()
