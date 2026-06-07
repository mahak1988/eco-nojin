"""
🔍 بررسی جامع ماژول آکادمی
مسیر: D:\econojin.com\apps\web\src\app\academy
"""
import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

print("=" * 80)
print("🔍 COMPREHENSIVE ACADEMY MODULE AUDIT")
print("=" * 80)
print(f"🕐 زمان بررسی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📂 مسیر: D:\\econojin.com\\apps\\web\\src\\app\\academy")

# ============================================================
# CONFIGURATION
# ============================================================
ACADEMY_PATH = Path('apps/web/src/app/academy')
LIB_PATH = Path('apps/web/src/lib/academy')
HOOKS_PATH = Path('apps/web/src/hooks/academy')
COMPONENTS_PATH = Path('apps/web/src/components/academy')

# ============================================================
# 1. FILE STRUCTURE ANALYSIS
# ============================================================
print("\n" + "=" * 80)
print("📂 1. FILE STRUCTURE ANALYSIS")
print("=" * 80)

file_stats = {
    'total_files': 0,
    'total_size': 0,
    'pages': [],
    'components': [],
    'by_type': defaultdict(int),
}

# Scan academy directory
if ACADEMY_PATH.exists():
    print(f"\n✅ Academy directory exists: {ACADEMY_PATH}")
    
    for file_path in ACADEMY_PATH.rglob('*'):
        if file_path.is_file():
            try:
                stat = file_path.stat()
                rel_path = file_path.relative_to(ACADEMY_PATH)
                
                file_stats['total_files'] += 1
                file_stats['total_size'] += stat.st_size
                file_stats['by_type'][file_path.suffix] += 1
                
                if file_path.name == 'page.tsx':
                    file_stats['pages'].append({
                        'path': str(rel_path),
                        'size': stat.st_size,
                        'full_path': file_path
                    })
                elif file_path.suffix in ['.tsx', '.ts']:
                    file_stats['components'].append({
                        'path': str(rel_path),
                        'size': stat.st_size,
                        'full_path': file_path
                    })
                
            except Exception as e:
                pass
    
    print(f"\n📊 Total Files: {file_stats['total_files']}")
    print(f"💾 Total Size: {file_stats['total_size']:,} bytes ({file_stats['total_size']/1024:.1f} KB)")
    
    print(f"\n📄 File Types:")
    for ext, count in sorted(file_stats['by_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {ext or '(no ext)':10} {count:5} files")
    
    print(f"\n📄 Pages ({len(file_stats['pages'])}):")
    for page in sorted(file_stats['pages'], key=lambda x: x['path']):
        size_kb = page['size'] / 1024
        print(f"   ✅ {page['path']:60} {size_kb:6.1f} KB")
    
    print(f"\n🧩 Components ({len(file_stats['components'])}):")
    for comp in sorted(file_stats['components'], key=lambda x: x['path'])[:20]:
        size_kb = comp['size'] / 1024
        print(f"   📦 {comp['path']:60} {size_kb:6.1f} KB")
    
else:
    print(f"❌ Academy directory NOT found: {ACADEMY_PATH}")

# ============================================================
# 2. CODE QUALITY ANALYSIS
# ============================================================
print("\n" + "=" * 80)
print("🔍 2. CODE QUALITY ANALYSIS")
print("=" * 80)

quality_issues = {
    'console_logs': [],
    'any_types': [],
    'todo_comments': [],
    'missing_error_handling': [],
    'hardcoded_strings': [],
    'large_files': [],
    'complex_functions': [],
}

code_stats = {
    'total_lines': 0,
    'total_functions': 0,
    'total_components': 0,
    'total_imports': 0,
    'total_exports': 0,
}

# Analyze all TypeScript/TSX files
all_ts_files = []
if ACADEMY_PATH.exists():
    all_ts_files.extend(ACADEMY_PATH.rglob('*.tsx'))
    all_ts_files.extend(ACADEMY_PATH.rglob('*.ts'))

# Add lib and hooks
if LIB_PATH.exists():
    all_ts_files.extend(LIB_PATH.rglob('*.ts'))
if HOOKS_PATH.exists():
    all_ts_files.extend(HOOKS_PATH.rglob('*.ts'))
if COMPONENTS_PATH.exists():
    all_ts_files.extend(COMPONENTS_PATH.rglob('*.tsx'))

print(f"\n📄 Analyzing {len(all_ts_files)} TypeScript files...")

for file_path in all_ts_files:
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        rel_path = str(file_path.relative_to(Path('apps/web/src')))
        
        code_stats['total_lines'] += len(lines)
        
        # Check file size
        if len(content) > 50000:  # 50KB
            quality_issues['large_files'].append({
                'file': rel_path,
                'size': len(content)
            })
        
        # Check console.log
        for i, line in enumerate(lines, 1):
            if 'console.log' in line and not line.strip().startswith('//'):
                quality_issues['console_logs'].append({
                    'file': rel_path,
                    'line': i,
                    'code': line.strip()[:80]
                })
        
        # Check 'any' type
        any_count = content.count(': any') + content.count('as any')
        if any_count > 0:
            quality_issues['any_types'].append({
                'file': rel_path,
                'count': any_count
            })
        
        # Check TODO/FIXME
        for i, line in enumerate(lines, 1):
            if 'TODO' in line or 'FIXME' in line:
                quality_issues['todo_comments'].append({
                    'file': rel_path,
                    'line': i,
                    'text': line.strip()[:80]
                })
        
        # Count functions and components
        code_stats['total_functions'] += len(re.findall(r'function\s+\w+', content))
        code_stats['total_components'] += len(re.findall(r'export (default )?function\s+\w+', content))
        code_stats['total_imports'] += len(re.findall(r'^import\s+', content, re.MULTILINE))
        code_stats['total_exports'] += len(re.findall(r'^export\s+', content, re.MULTILINE))
        
        # Check for missing error handling in API calls
        if 'fetch(' in content or 'api.get' in content or 'api.post' in content:
            if 'try {' not in content or 'catch' not in content:
                quality_issues['missing_error_handling'].append({
                    'file': rel_path
                })
        
        # Check for hardcoded strings (URLs, emails)
        if re.search(r'https?://[^\s"\']+', content):
            urls = re.findall(r'https?://[^\s"\']+', content)
            for url in urls:
                if 'localhost' not in url and 'econojin' not in url:
                    quality_issues['hardcoded_strings'].append({
                        'file': rel_path,
                        'type': 'URL',
                        'value': url[:50]
                    })
        
    except Exception as e:
        pass

print(f"\n📊 Code Statistics:")
print(f"   📝 Total Lines: {code_stats['total_lines']:,}")
print(f"   🔧 Total Functions: {code_stats['total_functions']}")
print(f"   🧩 Total Components: {code_stats['total_components']}")
print(f"   📥 Total Imports: {code_stats['total_imports']}")
print(f"   📤 Total Exports: {code_stats['total_exports']}")

print(f"\n🐛 Console.log statements: {len(quality_issues['console_logs'])}")
for issue in quality_issues['console_logs'][:5]:
    print(f"   ⚠️  {issue['file']}:{issue['line']} - {issue['code']}")

print(f"\n⚠️  'any' type usage: {sum(i['count'] for i in quality_issues['any_types'])} times")
for issue in quality_issues['any_types'][:5]:
    print(f"   ⚠️  {issue['file']}: {issue['count']} times")

print(f"\n📝 TODO/FIXME comments: {len(quality_issues['todo_comments'])}")
for issue in quality_issues['todo_comments'][:5]:
    print(f"   📝 {issue['file']}:{issue['line']} - {issue['text']}")

print(f"\n🛡️  Missing error handling: {len(quality_issues['missing_error_handling'])} files")
for issue in quality_issues['missing_error_handling'][:5]:
    print(f"   ⚠️  {issue['file']}")

print(f"\n🔗 Hardcoded external URLs: {len(quality_issues['hardcoded_strings'])}")
for issue in quality_issues['hardcoded_strings'][:5]:
    print(f"   ⚠️  {issue['file']}: {issue['value']}")

print(f"\n📦 Large files (>50KB): {len(quality_issues['large_files'])}")
for issue in quality_issues['large_files']:
    print(f"   ⚠️  {issue['file']}: {issue['size']/1024:.1f} KB")

# ============================================================
# 3. COMPONENT ANALYSIS
# ============================================================
print("\n" + "=" * 80)
print("🧩 3. COMPONENT ANALYSIS")
print("=" * 80)

component_analysis = {
    'buttons': 0,
    'buttons_with_handlers': 0,
    'links': 0,
    'internal_links': 0,
    'external_links': 0,
    'forms': 0,
    'forms_with_submit': 0,
    'images': 0,
    'images_with_alt': 0,
    'hooks_used': set(),
    'api_calls': 0,
}

for file_path in all_ts_files:
    if file_path.suffix != '.tsx':
        continue
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Count buttons
        buttons = re.findall(r'<button[^>]*>', content)
        component_analysis['buttons'] += len(buttons)
        component_analysis['buttons_with_handlers'] += sum(1 for b in buttons if 'onClick' in b)
        
        # Count links
        links = re.findall(r'<Link[^>]*href=["\']([^"\']+)["\']', content)
        component_analysis['links'] += len(links)
        for link in links:
            if link.startswith('/'):
                component_analysis['internal_links'] += 1
            else:
                component_analysis['external_links'] += 1
        
        # Count forms
        forms = re.findall(r'<form[^>]*>', content)
        component_analysis['forms'] += len(forms)
        component_analysis['forms_with_submit'] += sum(1 for f in forms if 'onSubmit' in f)
        
        # Count images
        images = re.findall(r'<img[^>]*>', content)
        component_analysis['images'] += len(images)
        component_analysis['images_with_alt'] += sum(1 for img in images if 'alt=' in img)
        
        # Find hooks
        hooks = re.findall(r'use(\w+)\(', content)
        component_analysis['hooks_used'].update(hooks)
        
        # Count API calls
        component_analysis['api_calls'] += len(re.findall(r'api\.(get|post|put|delete|patch)', content))
        
    except:
        pass

print(f"\n🔘 Buttons:")
print(f"   Total: {component_analysis['buttons']}")
print(f"   ✅ With onClick: {component_analysis['buttons_with_handlers']}")
print(f"   ⚠️  Without onClick: {component_analysis['buttons'] - component_analysis['buttons_with_handlers']}")

print(f"\n🔗 Links:")
print(f"   Total: {component_analysis['links']}")
print(f"   🏠 Internal: {component_analysis['internal_links']}")
print(f"   🌐 External: {component_analysis['external_links']}")

print(f"\n📝 Forms:")
print(f"   Total: {component_analysis['forms']}")
print(f"   ✅ With onSubmit: {component_analysis['forms_with_submit']}")

print(f"\n🖼️  Images:")
print(f"   Total: {component_analysis['images']}")
print(f"   ✅ With alt: {component_analysis['images_with_alt']}")

print(f"\n🪝 Hooks Used:")
for hook in sorted(component_analysis['hooks_used']):
    print(f"   • use{hook}")

print(f"\n🔌 API Calls: {component_analysis['api_calls']}")

# ============================================================
# 4. IMPORTS & DEPENDENCIES
# ============================================================
print("\n" + "=" * 80)
print("📥 4. IMPORTS & DEPENDENCIES")
print("=" * 80)

import_stats = defaultdict(int)
external_packages = set()

for file_path in all_ts_files:
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Find all imports
        imports = re.findall(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]", content)
        for imp in imports:
            import_stats[imp] += 1
            
            # Track external packages
            if not imp.startswith('.') and not imp.startswith('@/') and not imp.startswith('@/'):
                package = imp.split('/')[0]
                if package.startswith('@'):
                    package = '/'.join(imp.split('/')[:2])
                external_packages.add(package)
        
    except:
        pass

print(f"\n📦 External Packages Used: {len(external_packages)}")
for pkg in sorted(external_packages):
    count = import_stats.get(pkg, 0)
    print(f"   📥 {pkg:30} {count:5} imports")

print(f"\n🔗 Internal Path Aliases:")
for imp, count in sorted(import_stats.items(), key=lambda x: x[1], reverse=True)[:15]:
    if imp.startswith('@/'):
        print(f"   🔗 {imp:40} {count:5} uses")

# ============================================================
# 5. PAGE ROUTES ANALYSIS
# ============================================================
print("\n" + "=" * 80)
print("🛣️  5. PAGE ROUTES ANALYSIS")
print("=" * 80)

routes = []
if ACADEMY_PATH.exists():
    for page_file in ACADEMY_PATH.rglob('page.tsx'):
        rel_path = page_file.relative_to(ACADEMY_PATH)
        route = '/' + str(rel_path.parent).replace('\\', '/')
        route = route.replace('[id]', ':id').replace('[lessonId]', ':lessonId')
        if route == '/.':
            route = '/'
        
        routes.append({
            'route': route,
            'file': str(rel_path),
            'size': page_file.stat().st_size
        })

print(f"\n🛣️  Routes Found: {len(routes)}")
for route in sorted(routes, key=lambda x: x['route']):
    size_kb = route['size'] / 1024
    print(f"   🌐 {route['route']:50} {size_kb:6.1f} KB")

# ============================================================
# 6. BACKEND INTEGRATION
# ============================================================
print("\n" + "=" * 80)
print("🔌 6. BACKEND INTEGRATION")
print("=" * 80)

# Check API client
api_client_path = LIB_PATH / 'api.ts'
if api_client_path.exists():
    content = api_client_path.read_text(encoding='utf-8')
    methods = re.findall(r'(\w+):\s*(?:async\s+)?\(', content)
    
    print(f"\n📞 API Client Methods: {len(methods)}")
    for method in methods:
        print(f"   • academyApi.{method}()")
    
    # Check error handling
    if 'try {' in content and 'catch' in content:
        print(f"\n✅ Error handling present")
    else:
        print(f"\n⚠️  Missing error handling")
else:
    print(f"\n❌ API client not found: {api_client_path}")

# Check hooks
hooks_file = HOOKS_PATH / 'useAcademy.ts'
if hooks_file.exists():
    content = hooks_file.read_text(encoding='utf-8')
    hooks = re.findall(r'export function (use\w+)', content)
    
    print(f"\n🪝 Custom Hooks: {len(hooks)}")
    for hook in hooks:
        print(f"   • {hook}")
else:
    print(f"\n❌ Hooks file not found: {hooks_file}")

# ============================================================
# 7. QUALITY SCORE
# ============================================================
print("\n" + "=" * 80)
print("📊 7. QUALITY SCORE")
print("=" * 80)

total_checks = 0
passed_checks = 0

# File structure
total_checks += 1
if len(file_stats['pages']) >= 7:
    passed_checks += 1

# Code quality
total_checks += 1
if len(quality_issues['console_logs']) == 0:
    passed_checks += 1

total_checks += 1
any_total = sum(i['count'] for i in quality_issues['any_types'])
if any_total <= 3:
    passed_checks += 1

total_checks += 1
if len(quality_issues['missing_error_handling']) == 0:
    passed_checks += 1

total_checks += 1
if component_analysis['buttons'] == component_analysis['buttons_with_handlers']:
    passed_checks += 1

total_checks += 1
if component_analysis['forms'] == component_analysis['forms_with_submit']:
    passed_checks += 1

score = (passed_checks / total_checks * 100) if total_checks > 0 else 0

print(f"\n🎯 Quality Score: {score:.1f}% ({passed_checks}/{total_checks} checks passed)")

if score >= 90:
    grade = "A+ 🏆"
elif score >= 80:
    grade = "A ✅"
elif score >= 70:
    grade = "B 👍"
elif score >= 60:
    grade = "C ⚠️"
else:
    grade = "D ❌"

print(f"📈 Grade: {grade}")

# ============================================================
# 8. RECOMMENDATIONS
# ============================================================
print("\n" + "=" * 80)
print("💡 8. RECOMMENDATIONS")
print("=" * 80)

recommendations = []

if any_total > 3:
    recommendations.append({
        'priority': 'HIGH',
        'issue': f'{any_total} "any" type usages',
        'action': 'Replace with proper TypeScript types'
    })

if quality_issues['console_logs']:
    recommendations.append({
        'priority': 'MEDIUM',
        'issue': f'{len(quality_issues["console_logs"])} console.log statements',
        'action': 'Remove or use proper logging library'
    })

if quality_issues['missing_error_handling']:
    recommendations.append({
        'priority': 'HIGH',
        'issue': f'{len(quality_issues["missing_error_handling"])} files without error handling',
        'action': 'Add try/catch blocks to API calls'
    })

if component_analysis['buttons'] > component_analysis['buttons_with_handlers']:
    diff = component_analysis['buttons'] - component_analysis['buttons_with_handlers']
    recommendations.append({
        'priority': 'MEDIUM',
        'issue': f'{diff} buttons without onClick handlers',
        'action': 'Add event handlers or disable buttons'
    })

if quality_issues['large_files']:
    recommendations.append({
        'priority': 'LOW',
        'issue': f'{len(quality_issues["large_files"])} large files (>50KB)',
        'action': 'Consider code splitting'
    })

if recommendations:
    for i, rec in enumerate(recommendations, 1):
        priority_color = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }.get(rec['priority'], '⚪')
        
        print(f"\n   {i}. {priority_color} [{rec['priority']}] {rec['issue']}")
        print(f"      → {rec['action']}")
else:
    print("\n   ✅ No major issues found!")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 80)
print("✅ ACADEMY MODULE AUDIT COMPLETE")
print("=" * 80)

print(f"\n📊 Summary:")
print(f"   📂 Files: {file_stats['total_files']}")
print(f"   💾 Size: {file_stats['total_size']/1024:.1f} KB")
print(f"   📝 Lines: {code_stats['total_lines']:,}")
print(f"   🧩 Components: {code_stats['total_components']}")
print(f"   🛣️  Routes: {len(routes)}")
print(f"   🎯 Score: {score:.1f}% ({grade})")