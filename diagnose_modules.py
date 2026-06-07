"""
Diagnose Module Status - Check what went wrong
"""
from pathlib import Path
import re

print("=" * 100)
print("DIAGNOSE MODULE STATUS")
print("=" * 100)

FRONTEND = Path('apps/web/src')
BACKEND = Path('api')

# ============================================================
# 1. CHECK ALL PAGE FILES
# ============================================================
print("\n1. Checking all page files...")

page_files = list(FRONTEND.rglob('page.tsx'))
print(f"Found {len(page_files)} page files\n")

problem_pages = []

for page_file in sorted(page_files):
    try:
        content = page_file.read_text(encoding='utf-8')
        rel_path = page_file.relative_to(FRONTEND)
        
        # Check file size
        size = len(content)
        
        # Check if file has actual content
        has_use_client = '"use client"' in content or "'use client'" in content
        has_import = 'import ' in content
        has_export = 'export default' in content or 'export function' in content
        has_jsx = '<' in content and '>' in content
        
        # Check for dashboard components
        has_dashboard = 'Dashboard' in content
        
        # Check for hooks
        has_hooks = 'use' in content and '(' in content
        
        # Determine status
        if size < 100:
            status = "EMPTY/VERY SMALL"
            problem_pages.append((rel_path, status, size))
        elif not has_export:
            status = "NO EXPORT"
            problem_pages.append((rel_path, status, size))
        elif not has_jsx:
            status = "NO JSX"
            problem_pages.append((rel_path, status, size))
        else:
            status = "OK"
        
        print(f"   {status:20} {str(rel_path):60} {size:6} bytes")
        
    except Exception as e:
        print(f"   [ERROR] {page_file}: {e}")

# ============================================================
# 2. CHECK SPECIFIC MODULE PAGES
# ============================================================
print("\n2. Checking specific module pages...")

module_pages = {
    'weather': FRONTEND / 'app' / 'weather' / 'page.tsx',
    'drought': FRONTEND / 'app' / 'drought' / 'page.tsx',
    'iot': FRONTEND / 'app' / 'iot' / 'page.tsx',
    'ecocoin': FRONTEND / 'app' / 'ecocoin' / 'page.tsx',
    'mrv': FRONTEND / 'app' / 'mrv' / 'page.tsx',
    'soil-water': FRONTEND / 'app' / 'soil-water' / 'page.tsx',
    'sentinel': FRONTEND / 'app' / 'sentinel' / 'page.tsx',
    'ai': FRONTEND / 'app' / 'ai' / 'page.tsx',
}

for module, page_path in module_pages.items():
    if page_path.exists():
        content = page_path.read_text(encoding='utf-8')
        size = len(content)
        
        # Check what's in the file
        has_weather = 'WeatherDashboard' in content or 'useWeather' in content
        has_drought = 'DroughtDashboard' in content or 'useDrought' in content
        has_iot = 'IoTDashboard' in content or 'useIoT' in content
        has_blockchain = 'BlockchainDashboard' in content or 'useBlockchain' in content
        has_forest = 'ForestDashboard' in content or 'useForest' in content
        has_soil = 'SoilDashboard' in content or 'useSoil' in content
        has_satellite = 'SatelliteDashboard' in content or 'useSatellite' in content
        has_ai = 'AIDashboard' in content or 'useAI' in content
        
        components = []
        if has_weather: components.append('Weather')
        if has_drought: components.append('Drought')
        if has_iot: components.append('IoT')
        if has_blockchain: components.append('Blockchain')
        if has_forest: components.append('Forest')
        if has_soil: components.append('Soil')
        if has_satellite: components.append('Satellite')
        if has_ai: components.append('AI')
        
        print(f"\n   {module:15} ({size:6} bytes)")
        print(f"      Components: {', '.join(components) if components else 'NONE'}")
        
        if size < 500:
            print(f"      [WARNING] File is very small - might be incomplete")
            print(f"      Content preview:")
            print(f"      {content[:200]}")
    else:
        print(f"\n   {module:15} [MISSING]")

# ============================================================
# 3. CHECK DASHBOARD COMPONENTS
# ============================================================
print("\n\n3. Checking dashboard components...")

dashboard_components = {
    'WeatherDashboard': FRONTEND / 'components' / 'weather' / 'WeatherDashboard.tsx',
    'SoilDashboard': FRONTEND / 'components' / 'soil' / 'SoilDashboard.tsx',
    'SatelliteDashboard': FRONTEND / 'components' / 'satellite' / 'SatelliteDashboard.tsx',
    'DroughtDashboard': FRONTEND / 'components' / 'drought' / 'DroughtDashboard.tsx',
    'ForestDashboard': FRONTEND / 'components' / 'forest' / 'ForestDashboard.tsx',
    'IoTDashboard': FRONTEND / 'components' / 'iot' / 'IoTDashboard.tsx',
    'BlockchainDashboard': FRONTEND / 'components' / 'blockchain' / 'BlockchainDashboard.tsx',
    'AIDashboard': FRONTEND / 'components' / 'ai' / 'AIDashboard.tsx',
}

for comp_name, comp_path in dashboard_components.items():
    if comp_path.exists():
        content = comp_path.read_text(encoding='utf-8')
        size = len(content)
        
        # Check if component uses hooks
        has_hooks = 'use' in content and '(' in content
        has_data = 'data' in content or 'response' in content
        
        status = "OK" if has_hooks and has_data else "INCOMPLETE"
        
        print(f"   {status:15} {comp_name:30} {size:6} bytes")
        
        if status == "INCOMPLETE":
            print(f"      [WARNING] Component might not be using hooks properly")
    else:
        print(f"   [MISSING]      {comp_name}")

# ============================================================
# 4. CHECK HOOKS
# ============================================================
print("\n4. Checking hooks...")

hooks = {
    'useWeather': FRONTEND / 'hooks' / 'weather' / 'useWeather.ts',
    'useSoil': FRONTEND / 'hooks' / 'soil' / 'useSoil.ts',
    'useSatellite': FRONTEND / 'hooks' / 'satellite' / 'useSatellite.ts',
    'useDrought': FRONTEND / 'hooks' / 'drought' / 'useDrought.ts',
    'useForest': FRONTEND / 'hooks' / 'forest' / 'useForest.ts',
    'useIoT': FRONTEND / 'hooks' / 'iot' / 'useIoT.ts',
    'useBlockchain': FRONTEND / 'hooks' / 'blockchain' / 'useBlockchain.ts',
    'useAI': FRONTEND / 'hooks' / 'ai' / 'useAI.ts',
}

for hook_name, hook_path in hooks.items():
    if hook_path.exists():
        content = hook_path.read_text(encoding='utf-8')
        size = len(content)
        
        has_query = 'useQuery' in content or 'useMutation' in content
        has_api = 'api.get' in content or 'api.post' in content
        
        status = "OK" if has_query and has_api else "INCOMPLETE"
        
        print(f"   {status:15} {hook_name:30} {size:6} bytes")
    else:
        print(f"   [MISSING]      {hook_name}")

# ============================================================
# 5. CHECK BACKUP FILES
# ============================================================
print("\n5. Checking for backup files...")

backup_files = list(FRONTEND.rglob('*.backup')) + list(FRONTEND.rglob('*.bak'))
if backup_files:
    print(f"Found {len(backup_files)} backup files:")
    for backup in backup_files:
        print(f"   {backup.relative_to(FRONTEND)}")
else:
    print("No backup files found")

# ============================================================
# 6. SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)

print(f"\nProblem pages: {len(problem_pages)}")
for page, status, size in problem_pages:
    print(f"   {status:20} {page} ({size} bytes)")

print("\n" + "=" * 100)
print("DIAGNOSIS COMPLETE")
print("=" * 100)