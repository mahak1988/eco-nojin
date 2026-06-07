import re
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set

print("=" * 80)
print("🔍 COMPREHENSIVE FRONTEND DEVELOPMENT ANALYSIS")
print("=" * 80)

frontend_path = Path('apps/web')
if not frontend_path.exists():
    print(f"❌ Frontend path not found: {frontend_path}")
    exit(1)

# Data structures
analysis = {
    'api_calls': defaultdict(list),
    'external_apis': set(),
    'internal_apis': set(),
    'missing_components': [],
    'incomplete_features': [],
    'buttons_needing_handlers': [],
    'forms_needing_validation': [],
    'todo_items': [],
    'mock_data': [],
    'broken_links': [],
    'missing_types': [],
    'performance_issues': [],
    'accessibility_issues': [],
    'security_concerns': [],
    'optimization_opportunities': [],
}

# Scan all files
print("\n📂 Scanning all files...")
all_files = list(frontend_path.rglob('*.ts')) + list(frontend_path.rglob('*.tsx'))
all_files = [f for f in all_files if 'node_modules' not in str(f) and '.next' not in str(f)]

print(f"   Found {len(all_files)} TypeScript files")

# Analyze each file
for file_path in all_files:
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        rel_path = str(file_path.relative_to(frontend_path))
        
        # 1. API Calls Analysis
        # Fetch calls
        fetch_pattern = r'fetch\([\'"]([^\'"]+)[\'"]\)'
        for match in re.finditer(fetch_pattern, content):
            url = match.group(1)
            if url.startswith('http'):
                analysis['external_apis'].add(url)
            else:
                analysis['internal_apis'].add(url)
            analysis['api_calls']['fetch'].append({
                'file': rel_path,
                'url': url,
                'line': next(i+1 for i, line in enumerate(lines) if url in line)
            })
        
        # Axios calls
        axios_pattern = r'(axios\.(?:get|post|put|delete|patch))\([\'"]([^\'"]+)[\'"]\)'
        for match in re.finditer(axios_pattern, content):
            method = match.group(1)
            url = match.group(2)
            analysis['api_calls']['axios'].append({
                'file': rel_path,
                'method': method,
                'url': url,
                'line': next(i+1 for i, line in enumerate(lines) if url in line)
            })
        
        # API client calls
        api_client_pattern = r'api\.(get|post|put|delete|patch)(\w+)\('
        for match in re.finditer(api_client_pattern, content):
            method = match.group(1)
            endpoint = match.group(2)
            analysis['api_calls']['api_client'].append({
                'file': rel_path,
                'method': method,
                'endpoint': endpoint,
                'line': next(i+1 for i, line in enumerate(lines) if f'api.{method}{endpoint}' in line)
            })
        
        # 2. Buttons without handlers
        if file_path.suffix == '.tsx':
            for i, line in enumerate(lines, 1):
                if '<button' in line and 'onClick' not in line and 'disabled' not in line:
                    context = '\n'.join(lines[max(0, i-2):min(len(lines), i+5)])
                    if 'onClick' not in context and '</button>' in context:
                        analysis['buttons_needing_handlers'].append({
                            'file': rel_path,
                            'line': i,
                            'context': line.strip()[:100]
                        })
        
        # 3. Forms without validation
        if file_path.suffix == '.tsx':
            for i, line in enumerate(lines, 1):
                if '<form' in line and 'onSubmit' not in line:
                    context = '\n'.join(lines[max(0, i-2):min(len(lines), i+5)])
                    if 'onSubmit' not in context and '</form>' in context:
                        analysis['forms_needing_validation'].append({
                            'file': rel_path,
                            'line': i
                        })
        
        # 4. TODO/FIXME comments
        for i, line in enumerate(lines, 1):
            if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                analysis['todo_items'].append({
                    'file': rel_path,
                    'line': i,
                    'comment': line.strip()[:100]
                })
        
        # 5. Mock data / hardcoded values
        mock_patterns = [
            r'const\s+mock\w+\s*=',
            r'const\s+dummy\w+\s*=',
            r'const\s+fake\w+\s*=',
            r'//\s*Mock',
            r'//\s*Dummy',
        ]
        for pattern in mock_patterns:
            if re.search(pattern, content):
                analysis['mock_data'].append({
                    'file': rel_path,
                    'pattern': pattern
                })
                break
        
        # 6. Missing type definitions
        any_count = content.count(': any') + content.count('as any')
        if any_count > 0:
            analysis['missing_types'].append({
                'file': rel_path,
                'count': any_count
            })
        
        # 7. Performance issues
        # Large inline functions
        if content.count('() => {') > 10:
            analysis['performance_issues'].append({
                'file': rel_path,
                'issue': 'Many inline arrow functions (consider useCallback)'
            })
        
        # Missing React.memo
        if file_path.suffix == '.tsx' and 'export default function' in content:
            if 'React.memo' not in content and 'memo(' not in content:
                analysis['performance_issues'].append({
                    'file': rel_path,
                    'issue': 'Component not wrapped in React.memo'
                })
        
        # 8. Accessibility issues
        if file_path.suffix == '.tsx':
            # Images without alt
            img_pattern = r'<img[^>]*(?!alt=)[^>]*>'
            if re.search(img_pattern, content):
                analysis['accessibility_issues'].append({
                    'file': rel_path,
                    'issue': 'Image without alt attribute'
                })
            
            # Buttons without aria-label
            button_pattern = r'<button[^>]*(?!aria-label=)[^>]*>\s*</button>'
            if re.search(button_pattern, content):
                analysis['accessibility_issues'].append({
                    'file': rel_path,
                    'issue': 'Button without aria-label'
                })
        
        # 9. Security concerns
        # Dangerous innerHTML
        if 'dangerouslySetInnerHTML' in content:
            analysis['security_concerns'].append({
                'file': rel_path,
                'issue': 'Using dangerouslySetInnerHTML (XSS risk)'
            })
        
        # Console.log in production
        if 'console.log' in content and 'test' not in rel_path:
            analysis['security_concerns'].append({
                'file': rel_path,
                'issue': 'console.log in code (remove for production)'
            })
        
        # 10. Optimization opportunities
        # Large files
        if len(content) > 50000:  # 50KB
            analysis['optimization_opportunities'].append({
                'file': rel_path,
                'issue': f'Large file ({len(content)} bytes) - consider splitting'
            })
        
        # Multiple exports
        export_count = content.count('export ')
        if export_count > 5:
            analysis['optimization_opportunities'].append({
                'file': rel_path,
                'issue': f'Many exports ({export_count}) - consider code splitting'
            })
        
    except Exception as e:
        print(f"⚠️  Error analyzing {file_path}: {e}")

# Generate report
print("\n" + "=" * 80)
print("📊 ANALYSIS REPORT")
print("=" * 80)

# API Calls
print("\n🔌 API CALLS ANALYSIS")
print("-" * 80)
print(f"External APIs: {len(analysis['external_apis'])}")
for api in sorted(analysis['external_apis']):
    print(f"   - {api}")

print(f"\nInternal APIs: {len(analysis['internal_apis'])}")
for api in sorted(analysis['internal_apis'])[:20]:
    print(f"   - {api}")
if len(analysis['internal_apis']) > 20:
    print(f"   ... and {len(analysis['internal_apis']) - 20} more")

print(f"\nAPI Client Methods: {len(analysis['api_calls']['api_client'])}")
api_endpoints = Counter(call['endpoint'] for call in analysis['api_calls']['api_client'])
for endpoint, count in api_endpoints.most_common(10):
    print(f"   - {endpoint}: {count} calls")

# Buttons & Forms
print("\n🔘 INTERACTIVE ELEMENTS")
print("-" * 80)
print(f"Buttons without onClick: {len(analysis['buttons_needing_handlers'])}")
if analysis['buttons_needing_handlers']:
    for btn in analysis['buttons_needing_handlers'][:10]:
        print(f"   - {btn['file']}:{btn['line']}")

print(f"\nForms without validation: {len(analysis['forms_needing_validation'])}")
for form in analysis['forms_needing_validation'][:10]:
    print(f"   - {form['file']}:{form['line']}")

# TODO Items
print("\n📝 TODO/FIXME ITEMS")
print("-" * 80)
print(f"Total TODOs: {len(analysis['todo_items'])}")
for todo in analysis['todo_items'][:15]:
    print(f"   - {todo['file']}:{todo['line']} - {todo['comment']}")

# Mock Data
print("\n🎭 MOCK DATA USAGE")
print("-" * 80)
print(f"Files with mock data: {len(analysis['mock_data'])}")
for mock in analysis['mock_data'][:10]:
    print(f"   - {mock['file']}")

# Type Safety
print("\n🔒 TYPE SAFETY")
print("-" * 80)
total_any = sum(item['count'] for item in analysis['missing_types'])
print(f"Total 'any' usage: {total_any} times in {len(analysis['missing_types'])} files")
for item in sorted(analysis['missing_types'], key=lambda x: x['count'], reverse=True)[:10]:
    print(f"   - {item['file']}: {item['count']} times")

# Performance
print("\n⚡ PERFORMANCE ISSUES")
print("-" * 80)
print(f"Issues found: {len(analysis['performance_issues'])}")
for issue in analysis['performance_issues'][:10]:
    print(f"   - {issue['file']}: {issue['issue']}")

# Accessibility
print("\n♿ ACCESSIBILITY ISSUES")
print("-" * 80)
print(f"Issues found: {len(analysis['accessibility_issues'])}")
for issue in analysis['accessibility_issues'][:10]:
    print(f"   - {issue['file']}: {issue['issue']}")

# Security
print("\n🔐 SECURITY CONCERNS")
print("-" * 80)
print(f"Concerns found: {len(analysis['security_concerns'])}")
for concern in analysis['security_concerns'][:10]:
    print(f"   - {concern['file']}: {concern['issue']}")

# Optimization
print("\n🚀 OPTIMIZATION OPPORTUNITIES")
print("-" * 80)
print(f"Opportunities: {len(analysis['optimization_opportunities'])}")
for opt in analysis['optimization_opportunities'][:10]:
    print(f"   - {opt['file']}: {opt['issue']}")

# Summary
print("\n" + "=" * 80)
print("📋 DEVELOPMENT ROADMAP")
print("=" * 80)

print("\n🎯 PRIORITY 1 - Critical (Fix Immediately)")
print("   1. Complete buttons without handlers:", len(analysis['buttons_needing_handlers']))
print("   2. Add form validation:", len(analysis['forms_needing_validation']))
print("   3. Replace mock data with real APIs:", len(analysis['mock_data']))
print("   4. Fix security concerns:", len(analysis['security_concerns']))

print("\n🎯 PRIORITY 2 - High (This Sprint)")
print("   1. Add type definitions (remove 'any'):", total_any)
print("   2. Implement TODO items:", len(analysis['todo_items']))
print("   3. Fix accessibility issues:", len(analysis['accessibility_issues']))
print("   4. Optimize performance:", len(analysis['performance_issues']))

print("\n🎯 PRIORITY 3 - Medium (Next Sprint)")
print("   1. Code splitting for large files")
print("   2. Add React.memo to components")
print("   3. Remove console.log statements")
print("   4. Add error boundaries")

print("\n🎯 PRIORITY 4 - Low (Backlog)")
print("   1. Add loading states")
print("   2. Add error handling")
print("   3. Add unit tests")
print("   4. Add E2E tests")

# API Integration Plan
print("\n" + "=" * 80)
print("🔌 API INTEGRATION PLAN")
print("=" * 80)

print("\n📡 Backend APIs (FastAPI)")
print("   Base URL: http://localhost:8000")
print("   Endpoints to integrate:")
print("   - /api/v1/dashboard/stats")
print("   - /api/v1/iot/stats")
print("   - /api/v1/ecocoin/wallets/me")
print("   - /api/v1/academy/statistics")
print("   - /api/v1/maintenance/stats")
print("   - /api/v1/mrv/stats")
print("   - /api/v1/drought/statistics")
print("   - /api/v1/financial/dashboard")
print("   - /api/v1/scientific/thresholds")

print("\n🌐 External APIs (If Needed)")
print("   - Weather: OpenWeatherMap API")
print("   - Maps: Google Maps / Leaflet")
print("   - Charts: Chart.js / Recharts")
print("   - AI: OpenAI API (for recommendations)")
print("   - Blockchain: Web3.js / Ethers.js")

print("\n📦 Required NPM Packages")
print("   Already installed:")
print("   ✅ @tanstack/react-query")
print("   ✅ axios")
print("   ✅ chart.js")
print("   ✅ react-chartjs-2")
print("   ✅ jspdf")
print("   ✅ html2canvas")
print("\n   Recommended to install:")
print("   ⬜ react-hook-form (form validation)")
print("   ⬜ zod (schema validation)")
print("   ⬜ @hookform/resolvers")
print("   ⬜ react-hot-toast (notifications)")
print("   ⬜ framer-motion (animations)")
print("   ⬜ react-icons (icons)")

print("\n" + "=" * 80)
print("✅ ANALYSIS COMPLETE")
print("=" * 80)
print("\n💡 Next Steps:")
print("1. Review this report")
print("2. Create GitHub issues for each priority")
print("3. Start with Priority 1 items")
print("4. Run: python generate_fix_scripts.py")