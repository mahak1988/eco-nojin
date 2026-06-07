"""
📚 آکادمی اکو نوژین - اسکریپت بررسی جامع
بررسی کامل ماژول آکادمی در فرانت‌اند و بک‌اند
"""
import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

print("=" * 80)
print("📚 AUDITING ACADEMY MODULE - COMPREHENSIVE ANALYSIS")
print("=" * 80)
print(f"🕐 زمان بررسی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================================
# CONFIGURATION
# ============================================================
ROOT = Path('.')
FRONTEND = ROOT / 'apps/web/src'
BACKEND = ROOT / 'api'

# Expected files structure
EXPECTED_FRONTEND = {
    'pages': [
        'app/academy/page.tsx',
        'app/academy/courses/[id]/page.tsx',
        'app/academy/courses/[id]/lessons/[lessonId]/page.tsx',
        'app/academy/create/page.tsx',
        'app/academy/my-courses/page.tsx',
        'app/academy/certificates/page.tsx',
        'app/academy/guide/page.tsx',
    ],
    'components': [
        'components/academy',
    ],
    'lib': [
        'lib/academy/api.ts',
    ],
    'hooks': [
        'hooks/academy/useAcademy.ts',
    ]
}

EXPECTED_BACKEND = {
    'router': 'api/modules/academy/router.py',
    'models': 'api/modules/academy/models.py',
    'init': 'api/modules/academy/__init__.py',
}

# ============================================================
# 1. FRONTEND STRUCTURE AUDIT
# ============================================================
print("\n" + "=" * 80)
print("📂 1. FRONTEND STRUCTURE AUDIT")
print("=" * 80)

frontend_stats = {
    'total_files': 0,
    'total_size': 0,
    'existing': [],
    'missing': [],
    'by_type': defaultdict(int)
}

print("\n📄 Pages:")
for page in EXPECTED_FRONTEND['pages']:
    full_path = FRONTEND / page
    if full_path.exists():
        size = full_path.stat().st_size
        frontend_stats['existing'].append(page)
        frontend_stats['total_files'] += 1
        frontend_stats['total_size'] += size
        frontend_stats['by_type']['page'] += 1
        print(f"   ✅ {page} ({size:,} bytes)")
    else:
        frontend_stats['missing'].append(page)
        print(f"   ❌ {page} [MISSING]")

print("\n🧩 Components:")
comp_path = FRONTEND / 'components/academy'
if comp_path.exists():
    comp_files = list(comp_path.rglob('*.tsx')) + list(comp_path.rglob('*.ts'))
    print(f"   ✅ components/academy/ ({len(comp_files)} files)")
    for cf in comp_files:
        print(f"      - {cf.relative_to(FRONTEND)}")
else:
    print(f"   ❌ components/academy/ [MISSING]")

print("\n🔌 API Client:")
api_path = FRONTEND / 'lib/academy/api.ts'
if api_path.exists():
    print(f"   ✅ lib/academy/api.ts")
else:
    print(f"   ❌ lib/academy/api.ts [MISSING]")

print("\n🪝 Hooks:")
hooks_path = FRONTEND / 'hooks/academy/useAcademy.ts'
if hooks_path.exists():
    print(f"   ✅ hooks/academy/useAcademy.ts")
else:
    print(f"   ❌ hooks/academy/useAcademy.ts [MISSING]")

# ============================================================
# 2. BACKEND STRUCTURE AUDIT
# ============================================================
print("\n" + "=" * 80)
print("🔧 2. BACKEND STRUCTURE AUDIT")
print("=" * 80)

backend_stats = {
    'router_exists': False,
    'models_exists': False,
    'registered_in_main': False,
    'endpoints': [],
    'response_models': []
}

# Check router
router_path = BACKEND / 'modules/academy/router.py'
if router_path.exists():
    backend_stats['router_exists'] = True
    content = router_path.read_text(encoding='utf-8-sig')
    
    # Find endpoints
    endpoint_pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
    matches = re.findall(endpoint_pattern, content)
    backend_stats['endpoints'] = matches
    
    # Find response models
    model_pattern = r'response_model=(\w+)'
    backend_stats['response_models'] = re.findall(model_pattern, content)
    
    print(f"   ✅ router.py ({len(content):,} bytes)")
    print(f"   📡 Endpoints found: {len(matches)}")
    for method, path in matches:
        print(f"      • {method.upper():6} /api/v1/academy{path}")
    
    print(f"   📦 Response models: {len(backend_stats['response_models'])}")
    for model in set(backend_stats['response_models']):
        print(f"      • {model}")
else:
    print(f"   ❌ router.py [MISSING]")

# Check models
models_path = BACKEND / 'modules/academy/models.py'
if models_path.exists():
    backend_stats['models_exists'] = True
    print(f"   ✅ models.py")
else:
    print(f"   ❌ models.py [MISSING]")

# Check registration in main.py
main_path = BACKEND / 'main.py'
if main_path.exists():
    main_content = main_path.read_text(encoding='utf-8-sig')
    if 'academy_router' in main_content:
        backend_stats['registered_in_main'] = True
        print(f"   ✅ Registered in main.py")
    else:
        print(f"   ❌ NOT registered in main.py")

# ============================================================
# 3. CODE QUALITY AUDIT
# ============================================================
print("\n" + "=" * 80)
print("🔍 3. CODE QUALITY AUDIT")
print("=" * 80)

quality_issues = {
    'broken_imports': [],
    'console_logs': [],
    'any_types': [],
    'hardcoded_data': [],
    'missing_error_handling': [],
    'todo_comments': []
}

# Scan all academy frontend files
academy_files = list((FRONTEND / 'app/academy').rglob('*.tsx')) + \
                list((FRONTEND / 'app/academy').rglob('*.ts')) + \
                ([FRONTEND / 'lib/academy/api.ts'] if (FRONTEND / 'lib/academy/api.ts').exists() else []) + \
                ([FRONTEND / 'hooks/academy/useAcademy.ts'] if (FRONTEND / 'hooks/academy/useAcademy.ts').exists() else [])

for file_path in academy_files:
    if not file_path.exists():
        continue
    
    try:
        content = file_path.read_text(encoding='utf-8')
        rel_path = str(file_path.relative_to(FRONTEND))
        lines = content.split('\n')
        
        # Check console.log
        for i, line in enumerate(lines, 1):
            if 'console.log' in line and not line.strip().startswith('//'):
                quality_issues['console_logs'].append({
                    'file': rel_path,
                    'line': i
                })
        
        # Check 'any' type usage
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
        
        # Check for hardcoded URLs (not localhost)
        if 'http://' in content and 'localhost' not in content:
            quality_issues['hardcoded_data'].append({
                'file': rel_path,
                'issue': 'External hardcoded URL'
            })
        
        # Check for missing error handling in fetch/axios
        if 'fetch(' in content or 'api.get' in content or 'api.post' in content:
            if 'catch' not in content and 'try' not in content:
                quality_issues['missing_error_handling'].append({
                    'file': rel_path
                })
    
    except Exception as e:
        print(f"   ⚠️  Error reading {file_path}: {e}")

print("\n🐛 Console.log statements:")
if quality_issues['console_logs']:
    for issue in quality_issues['console_logs'][:10]:
        print(f"   ⚠️  {issue['file']}:{issue['line']}")
else:
    print("   ✅ No console.log found")

print("\n⚠️  'any' type usage:")
if quality_issues['any_types']:
    for issue in quality_issues['any_types'][:10]:
        print(f"   ⚠️  {issue['file']}: {issue['count']} times")
else:
    print("   ✅ No 'any' types found")

print("\n📝 TODO/FIXME comments:")
if quality_issues['todo_comments']:
    for issue in quality_issues['todo_comments'][:10]:
        print(f"   📝 {issue['file']}:{issue['line']} - {issue['text']}")
else:
    print("   ✅ No TODO/FIXME comments")

print("\n🔗 Hardcoded external URLs:")
if quality_issues['hardcoded_data']:
    for issue in quality_issues['hardcoded_data']:
        print(f"   ⚠️  {issue['file']}: {issue['issue']}")
else:
    print("   ✅ No hardcoded external URLs")

print("\n🛡️  Missing error handling:")
if quality_issues['missing_error_handling']:
    for issue in quality_issues['missing_error_handling']:
        print(f"   ⚠️  {issue['file']}")
else:
    print("   ✅ All API calls have error handling")

# ============================================================
# 4. CONTENT AUDIT
# ============================================================
print("\n" + "=" * 80)
print("📖 4. CONTENT AUDIT")
print("=" * 80)

content_stats = {
    'total_buttons': 0,
    'buttons_with_handlers': 0,
    'total_links': 0,
    'internal_links': 0,
    'external_links': 0,
    'forms': 0,
    'forms_with_submit': 0,
    'images': 0,
    'images_with_alt': 0,
}

for file_path in academy_files:
    if not file_path.exists() or file_path.suffix != '.tsx':
        continue
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Count buttons
        buttons = re.findall(r'<button[^>]*>', content)
        content_stats['total_buttons'] += len(buttons)
        content_stats['buttons_with_handlers'] += sum(1 for b in buttons if 'onClick' in b)
        
        # Count links
        links = re.findall(r'<Link[^>]*href=["\']([^"\']+)["\']', content)
        content_stats['total_links'] += len(links)
        for link in links:
            if link.startswith('/'):
                content_stats['internal_links'] += 1
            else:
                content_stats['external_links'] += 1
        
        # Count forms
        forms = re.findall(r'<form[^>]*>', content)
        content_stats['forms'] += len(forms)
        content_stats['forms_with_submit'] += sum(1 for f in forms if 'onSubmit' in f)
        
        # Count images
        images = re.findall(r'<img[^>]*>', content)
        content_stats['images'] += len(images)
        content_stats['images_with_alt'] += sum(1 for img in images if 'alt=' in img)
    
    except Exception as e:
        pass

print(f"\n🔘 Buttons: {content_stats['total_buttons']} total")
print(f"   ✅ With onClick: {content_stats['buttons_with_handlers']}")
print(f"   ⚠️  Without onClick: {content_stats['total_buttons'] - content_stats['buttons_with_handlers']}")

print(f"\n🔗 Links: {content_stats['total_links']} total")
print(f"   🏠 Internal: {content_stats['internal_links']}")
print(f"   🌐 External: {content_stats['external_links']}")

print(f"\n📝 Forms: {content_stats['forms']} total")
print(f"   ✅ With onSubmit: {content_stats['forms_with_submit']}")

print(f"\n🖼️  Images: {content_stats['images']} total")
print(f"   ✅ With alt: {content_stats['images_with_alt']}")

# ============================================================
# 5. API ENDPOINT AUDIT
# ============================================================
print("\n" + "=" * 80)
print("🔌 5. API ENDPOINT AUDIT")
print("=" * 80)

# Check if backend is running
try:
    import urllib.request
    import urllib.error
    
    try:
        with urllib.request.urlopen('http://localhost:8000/openapi.json', timeout=2) as response:
            openapi = json.loads(response.read().decode())
            backend_running = True
            
            # Find academy endpoints
            academy_endpoints = [
                path for path in openapi.get('paths', {}).keys()
                if '/academy' in path
            ]
            
            print(f"\n🟢 Backend is RUNNING on port 8000")
            print(f"📡 Academy endpoints in OpenAPI: {len(academy_endpoints)}")
            for ep in academy_endpoints:
                methods = list(openapi['paths'][ep].keys())
                print(f"   • {', '.join(m.upper() for m in methods):6} {ep}")
    
    except urllib.error.URLError:
        backend_running = False
        print("\n🔴 Backend is NOT running on port 8000")
        print("   💡 Start with: uvicorn api.main:app --reload --port 8000")

except Exception as e:
    backend_running = False
    print(f"\n⚠️  Could not check backend: {e}")

# Check frontend API client
api_client_path = FRONTEND / 'lib/academy/api.ts'
if api_client_path.exists():
    api_content = api_client_path.read_text(encoding='utf-8')
    api_methods = re.findall(r'(\w+):\s*\(', api_content)
    print(f"\n📞 Frontend API methods: {len(api_methods)}")
    for method in api_methods:
        print(f"   • academyApi.{method}()")

# ============================================================
# 6. NAVIGATION AUDIT
# ============================================================
print("\n" + "=" * 80)
print("🧭 6. NAVIGATION AUDIT")
print("=" * 80)

# Check if academy is in main navigation
navbar_paths = [
    FRONTEND / 'components/layout/Navbar.tsx',
    FRONTEND / 'components/layout/navbar.tsx',
    FRONTEND / 'app/Navbar.tsx',
]

navbar_found = False
for nav_path in navbar_paths:
    if nav_path.exists():
        navbar_found = True
        content = nav_path.read_text(encoding='utf-8')
        if '/academy' in content:
            print(f"   ✅ Academy link found in {nav_path.name}")
        else:
            print(f"   ⚠️  Academy link NOT in {nav_path.name}")
        break

if not navbar_found:
    print("   ⚠️  Navbar file not found in common locations")

# Check internal links validity
print("\n🔗 Internal link targets:")
internal_links_checked = set()
for file_path in academy_files:
    if not file_path.exists() or file_path.suffix != '.tsx':
        continue
    
    try:
        content = file_path.read_text(encoding='utf-8')
        links = re.findall(r'href=["\'](/academy[^"\']*)["\']', content)
        for link in links:
            if link not in internal_links_checked:
                internal_links_checked.add(link)
                # Check if target page exists
                target_path = link.replace('/academy', 'app/academy')
                if '[id]' in target_path or '[lessonId]' in target_path:
                    print(f"   ✅ {link} (dynamic route)")
                elif (FRONTEND / target_path / 'page.tsx').exists():
                    print(f"   ✅ {link}")
                else:
                    print(f"   ❌ {link} [TARGET MISSING]")
    except:
        pass

# ============================================================
# 7. SUMMARY & RECOMMENDATIONS
# ============================================================
print("\n" + "=" * 80)
print("📊 7. SUMMARY & RECOMMENDATIONS")
print("=" * 80)

# Calculate scores
total_checks = 0
passed_checks = 0

# Frontend structure
for page in EXPECTED_FRONTEND['pages']:
    total_checks += 1
    if (FRONTEND / page).exists():
        passed_checks += 1

# Backend structure
total_checks += 3
if backend_stats['router_exists']: passed_checks += 1
if backend_stats['models_exists']: passed_checks += 1
if backend_stats['registered_in_main']: passed_checks += 1

# Quality
total_checks += 3
if not quality_issues['console_logs']: passed_checks += 1
if not quality_issues['any_types']: passed_checks += 1
if not quality_issues['missing_error_handling']: passed_checks += 1

# Backend running
total_checks += 1
if backend_running: passed_checks += 1

score = (passed_checks / total_checks * 100) if total_checks > 0 else 0

print(f"\n🎯 Overall Score: {score:.1f}% ({passed_checks}/{total_checks} checks passed)")

# Grade
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

# Recommendations
print("\n💡 RECOMMENDATIONS:")

recommendations = []

if frontend_stats['missing']:
    recommendations.append({
        'priority': 'HIGH',
        'issue': f'{len(frontend_stats["missing"])} pages missing',
        'action': 'Create missing pages'
    })

if not backend_stats['router_exists']:
    recommendations.append({
        'priority': 'CRITICAL',
        'issue': 'Backend router missing',
        'action': 'Create api/modules/academy/router.py'
    })

if not backend_stats['registered_in_main']:
    recommendations.append({
        'priority': 'HIGH',
        'issue': 'Router not registered in main.py',
        'action': 'Add academy_router to api/main.py'
    })

if not backend_running:
    recommendations.append({
        'priority': 'HIGH',
        'issue': 'Backend not running',
        'action': 'Start uvicorn api.main:app --reload --port 8000'
    })

if quality_issues['console_logs']:
    recommendations.append({
        'priority': 'MEDIUM',
        'issue': f'{len(quality_issues["console_logs"])} console.log statements',
        'action': 'Remove or replace with proper logging'
    })

if quality_issues['any_types']:
    total_any = sum(i['count'] for i in quality_issues['any_types'])
    recommendations.append({
        'priority': 'MEDIUM',
        'issue': f'{total_any} "any" type usages',
        'action': 'Replace with proper TypeScript types'
    })

if quality_issues['missing_error_handling']:
    recommendations.append({
        'priority': 'MEDIUM',
        'issue': 'API calls without error handling',
        'action': 'Add try/catch blocks'
    })

if content_stats['total_buttons'] > content_stats['buttons_with_handlers']:
    diff = content_stats['total_buttons'] - content_stats['buttons_with_handlers']
    recommendations.append({
        'priority': 'MEDIUM',
        'issue': f'{diff} buttons without onClick handlers',
        'action': 'Add event handlers or disable buttons'
    })

# Sort by priority
priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
recommendations.sort(key=lambda x: priority_order.get(x['priority'], 99))

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

# File statistics
print("\n" + "=" * 80)
print("📈 FILE STATISTICS")
print("=" * 80)
print(f"   Total frontend files: {frontend_stats['total_files']}")
print(f"   Total size: {frontend_stats['total_size']:,} bytes ({frontend_stats['total_size']/1024:.1f} KB)")
print(f"   Backend endpoints: {len(backend_stats['endpoints'])}")
print(f"   Response models: {len(set(backend_stats['response_models']))}")

print("\n" + "=" * 80)
print("✅ ACADEMY MODULE AUDIT COMPLETE")
print("=" * 80)