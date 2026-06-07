import re
import os
from pathlib import Path
from collections import defaultdict

print("=" * 80)
print("🔍 FRONTEND COMPREHENSIVE ANALYSIS")
print("=" * 80)

frontend_path = Path('apps/web')
if not frontend_path.exists():
    print(f"❌ Frontend path not found: {frontend_path}")
    exit(1)

# Statistics
stats = {
    'total_files': 0,
    'ts_files': 0,
    'tsx_files': 0,
    'components': 0,
    'pages': 0,
    'hooks': 0,
    'utils': 0,
}

# Issues
issues = {
    'syntax_errors': [],
    'broken_imports': [],
    'missing_modules': [],
    'incomplete_components': [],
    'buttons_without_handlers': [],
    'todo_comments': [],
    'console_logs': [],
    'any_types': [],
    'empty_functions': [],
}

# Scan all TypeScript files
print("\n📂 Scanning files...")
for ext in ['*.ts', '*.tsx']:
    for file_path in frontend_path.rglob(ext):
        # Skip node_modules and .next
        if 'node_modules' in str(file_path) or '.next' in str(file_path):
            continue
        
        stats['total_files'] += 1
        if file_path.suffix == '.ts':
            stats['ts_files'] += 1
        else:
            stats['tsx_files'] += 1
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check for syntax errors (backslash issues)
            if r'className={\ \ \}' in content or r'className={\ ' in content:
                issues['syntax_errors'].append({
                    'file': str(file_path.relative_to(frontend_path)),
                    'line': next(i+1 for i, line in enumerate(lines) if r'className={\ ' in line),
                    'issue': 'Broken backticks in className'
                })
            
            # Check for broken imports
            import_pattern = r"import\s+.*from\s+['\"]([^'\"]+)['\"]"
            for match in re.finditer(import_pattern, content):
                import_path = match.group(1)
                if import_path.startswith('.') or import_path.startswith('@'):
                    # Check if file exists
                    if import_path.startswith('@'):
                        actual_path = frontend_path / 'src' / import_path[2:]
                    else:
                        actual_path = file_path.parent / import_path
                    
                    # Add extensions
                    possible_paths = [
                        actual_path,
                        actual_path.with_suffix('.ts'),
                        actual_path.with_suffix('.tsx'),
                        actual_path / 'index.ts',
                        actual_path / 'index.tsx',
                    ]
                    
                    if not any(p.exists() for p in possible_paths):
                        issues['broken_imports'].append({
                            'file': str(file_path.relative_to(frontend_path)),
                            'import': import_path,
                            'line': next(i+1 for i, line in enumerate(lines) if import_path in line)
                        })
            
            # Check for TODO comments
            for i, line in enumerate(lines, 1):
                if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                    issues['todo_comments'].append({
                        'file': str(file_path.relative_to(frontend_path)),
                        'line': i,
                        'comment': line.strip()
                    })
            
            # Check for console.log
            for i, line in enumerate(lines, 1):
                if 'console.log' in line and not line.strip().startswith('//'):
                    issues['console_logs'].append({
                        'file': str(file_path.relative_to(frontend_path)),
                        'line': i
                    })
            
            # Check for 'any' type usage
            for i, line in enumerate(lines, 1):
                if ': any' in line or 'as any' in line:
                    issues['any_types'].append({
                        'file': str(file_path.relative_to(frontend_path)),
                        'line': i
                    })
            
            # Check for buttons without onClick
            if file_path.suffix == '.tsx':
                button_pattern = r'<button[^>]*>(?!.*onClick)'
                for i, line in enumerate(lines, 1):
                    if '<button' in line and 'onClick' not in line and 'disabled' not in line:
                        # Check next few lines too
                        context = '\n'.join(lines[i-1:min(i+5, len(lines))])
                        if 'onClick' not in context:
                            issues['buttons_without_handlers'].append({
                                'file': str(file_path.relative_to(frontend_path)),
                                'line': i
                            })
            
            # Check for empty functions
            for i, line in enumerate(lines, 1):
                if re.search(r'function\s+\w+\s*\([^)]*\)\s*{\s*}', line):
                    issues['empty_functions'].append({
                        'file': str(file_path.relative_to(frontend_path)),
                        'line': i
                    })
            
            # Categorize files
            if 'components' in str(file_path):
                stats['components'] += 1
            elif 'app' in str(file_path) and 'page.tsx' in str(file_path):
                stats['pages'] += 1
            elif 'hooks' in str(file_path):
                stats['hooks'] += 1
            elif 'lib' in str(file_path) or 'utils' in str(file_path):
                stats['utils'] += 1
                
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")

# Print statistics
print("\n" + "=" * 80)
print("📊 FILE STATISTICS")
print("=" * 80)
print(f"Total Files: {stats['total_files']}")
print(f"  - TypeScript (.ts): {stats['ts_files']}")
print(f"  - TSX (.tsx): {stats['tsx_files']}")
print(f"  - Components: {stats['components']}")
print(f"  - Pages: {stats['pages']}")
print(f"  - Hooks: {stats['hooks']}")
print(f"  - Utils/Lib: {stats['utils']}")

# Print issues
print("\n" + "=" * 80)
print("🚨 ISSUES FOUND")
print("=" * 80)

if issues['syntax_errors']:
    print(f"\n❌ Syntax Errors: {len(issues['syntax_errors'])}")
    for issue in issues['syntax_errors'][:10]:
        print(f"   - {issue['file']}:{issue['line']} - {issue['issue']}")

if issues['broken_imports']:
    print(f"\n⚠️  Broken Imports: {len(issues['broken_imports'])}")
    for issue in issues['broken_imports'][:10]:
        print(f"   - {issue['file']}:{issue['line']} - Cannot find '{issue['import']}'")

if issues['buttons_without_handlers']:
    print(f"\n🔘 Buttons Without Handlers: {len(issues['buttons_without_handlers'])}")
    for issue in issues['buttons_without_handlers'][:10]:
        print(f"   - {issue['file']}:{issue['line']}")

if issues['todo_comments']:
    print(f"\n📝 TODO Comments: {len(issues['todo_comments'])}")
    for issue in issues['todo_comments'][:10]:
        print(f"   - {issue['file']}:{issue['line']} - {issue['comment'][:50]}")

if issues['console_logs']:
    print(f"\n🔍 Console Logs: {len(issues['console_logs'])}")
    for issue in issues['console_logs'][:10]:
        print(f"   - {issue['file']}:{issue['line']}")

if issues['any_types']:
    print(f"\n⚠️  'any' Type Usage: {len(issues['any_types'])}")
    for issue in issues['any_types'][:10]:
        print(f"   - {issue['file']}:{issue['line']}")

if issues['empty_functions']:
    print(f"\n📦 Empty Functions: {len(issues['empty_functions'])}")
    for issue in issues['empty_functions'][:10]:
        print(f"   - {issue['file']}:{issue['line']}")

# Summary
print("\n" + "=" * 80)
print("📋 SUMMARY")
print("=" * 80)
total_issues = sum(len(v) for v in issues.values())
print(f"Total Issues: {total_issues}")
print(f"  - Critical (Syntax Errors): {len(issues['syntax_errors'])}")
print(f"  - High (Broken Imports): {len(issues['broken_imports'])}")
print(f"  - Medium (Empty Functions): {len(issues['empty_functions'])}")
print(f"  - Low (TODO/Console): {len(issues['todo_comments']) + len(issues['console_logs'])}")

print("\n✅ Analysis complete!")
print("💡 Run: python fix_layout.py to fix the critical syntax error")