"""
🔍 بررسی جامع پیاده‌سازی سه فاز و شناسایی فایل‌های یتیم
"""
import re
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

print("=" * 100)
print("🔍 COMPREHENSIVE PHASE IMPLEMENTATION & ORPHAN FILES AUDIT")
print("=" * 100)
print(f"🕐 زمان بررسی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

ROOT = Path('.')
BACKEND = ROOT / 'api'
FRONTEND = ROOT / 'apps/web/src'

# ============================================================
# 1. PHASE 1 FILES CHECK
# ============================================================
print("\n" + "=" * 100)
print("📦 PHASE 1: Weather, Soil, Sentinel-2")
print("=" * 100)

phase1_files = {
    'backend_services': [
        'api/services/weather/open_meteo.py',
        'api/services/soil/soilgrids.py',
        'api/services/satellite/sentinel2.py',
    ],
    'frontend_hooks': [
        'apps/web/src/hooks/weather/useWeather.ts',
        'apps/web/src/hooks/soil/useSoil.ts',
        'apps/web/src/hooks/satellite/useSatellite.ts',
    ]
}

phase1_status = {'exists': [], 'missing': [], 'imported': [], 'not_imported': []}

print("\n📂 Backend Services:")
for file_path in phase1_files['backend_services']:
    full_path = ROOT / file_path
    if full_path.exists():
        phase1_status['exists'].append(file_path)
        size = full_path.stat().st_size
        print(f"   ✅ {file_path} ({size:,} bytes)")
        
        # Check if imported in router
        service_name = Path(file_path).stem
        router_files = list((BACKEND / 'modules').rglob('router.py'))
        imported = False
        for router in router_files:
            content = router.read_text(encoding='utf-8-sig')
            if service_name in content:
                imported = True
                phase1_status['imported'].append(file_path)
                print(f"      ✅ Imported in {router.relative_to(ROOT)}")
                break
        
        if not imported:
            phase1_status['not_imported'].append(file_path)
            print(f"      ⚠️  Not imported in any router")
    else:
        phase1_status['missing'].append(file_path)
        print(f"   ❌ {file_path} [MISSING]")

print("\n🎨 Frontend Hooks:")
for file_path in phase1_files['frontend_hooks']:
    full_path = ROOT / file_path
    if full_path.exists():
        phase1_status['exists'].append(file_path)
        size = full_path.stat().st_size
        print(f"   ✅ {file_path} ({size:,} bytes)")
        
        # Check if used in components
        hook_name = Path(file_path).stem
        used = False
        for tsx_file in (FRONTEND / 'app').rglob('*.tsx'):
            content = tsx_file.read_text(encoding='utf-8')
            if hook_name in content:
                used = True
                print(f"      ✅ Used in {tsx_file.relative_to(ROOT)}")
                break
        
        if not used:
            print(f"      ⚠️  Not used in any component")
    else:
        phase1_status['missing'].append(file_path)
        print(f"   ❌ {file_path} [MISSING]")

# ============================================================
# 2. PHASE 2 FILES CHECK
# ============================================================
print("\n" + "=" * 100)
print("📦 PHASE 2: Drought, Landsat, MODIS, GEDI")
print("=" * 100)

phase2_files = {
    'backend_services': [
        'api/services/drought/chirps.py',
        'api/services/drought/spei.py',
        'api/services/satellite/landsat.py',
        'api/services/satellite/modis.py',
        'api/services/satellite/gedi.py',
    ],
    'frontend_hooks': [
        'apps/web/src/hooks/drought/useDrought.ts',
        'apps/web/src/hooks/forest/useForest.ts',
    ]
}

phase2_status = {'exists': [], 'missing': [], 'imported': [], 'not_imported': []}

print("\n📂 Backend Services:")
for file_path in phase2_files['backend_services']:
    full_path = ROOT / file_path
    if full_path.exists():
        phase2_status['exists'].append(file_path)
        size = full_path.stat().st_size
        print(f"   ✅ {file_path} ({size:,} bytes)")
        
        service_name = Path(file_path).stem
        router_files = list((BACKEND / 'modules').rglob('router.py'))
        imported = False
        for router in router_files:
            content = router.read_text(encoding='utf-8-sig')
            if service_name in content:
                imported = True
                phase2_status['imported'].append(file_path)
                print(f"      ✅ Imported in {router.relative_to(ROOT)}")
                break
        
        if not imported:
            phase2_status['not_imported'].append(file_path)
            print(f"      ⚠️  Not imported in any router")
    else:
        phase2_status['missing'].append(file_path)
        print(f"   ❌ {file_path} [MISSING]")

print("\n🎨 Frontend Hooks:")
for file_path in phase2_files['frontend_hooks']:
    full_path = ROOT / file_path
    if full_path.exists():
        phase2_status['exists'].append(file_path)
        size = full_path.stat().st_size
        print(f"   ✅ {file_path} ({size:,} bytes)")
        
        hook_name = Path(file_path).stem
        used = False
        for tsx_file in (FRONTEND / 'app').rglob('*.tsx'):
            content = tsx_file.read_text(encoding='utf-8')
            if hook_name in content:
                used = True
                print(f"      ✅ Used in {tsx_file.relative_to(ROOT)}")
                break
        
        if not used:
            print(f"      ⚠️  Not used in any component")
    else:
        phase2_status['missing'].append(file_path)
        print(f"   ❌ {file_path} [MISSING]")

# ============================================================
# 3. PHASE 3 FILES CHECK
# ============================================================
print("\n" + "=" * 100)
print("📦 PHASE 3: IoT, Blockchain, AI")
print("=" * 100)

phase3_files = {
    'backend_services': [
        'api/services/iot/mqtt_service.py',
        'api/services/blockchain/blockchain.py',
        'api/services/ai/ai_service.py',
    ],
    'frontend_hooks': [
        'apps/web/src/hooks/iot/useIoT.ts',
        'apps/web/src/hooks/blockchain/useBlockchain.ts',
        'apps/web/src/hooks/ai/useAI.ts',
    ]
}

phase3_status = {'exists': [], 'missing': [], 'imported': [], 'not_imported': []}

print("\n📂 Backend Services:")
for file_path in phase3_files['backend_services']:
    full_path = ROOT / file_path
    if full_path.exists():
        phase3_status['exists'].append(file_path)
        size = full_path.stat().st_size
        print(f"   ✅ {file_path} ({size:,} bytes)")
        
        service_name = Path(file_path).stem
        router_files = list((BACKEND / 'modules').rglob('router.py'))
        imported = False
        for router in router_files:
            content = router.read_text(encoding='utf-8-sig')
            if service_name in content:
                imported = True
                phase3_status['imported'].append(file_path)
                print(f"      ✅ Imported in {router.relative_to(ROOT)}")
                break
        
        if not imported:
            phase3_status['not_imported'].append(file_path)
            print(f"      ⚠️  Not imported in any router")
    else:
        phase3_status['missing'].append(file_path)
        print(f"   ❌ {file_path} [MISSING]")

print("\n🎨 Frontend Hooks:")
for file_path in phase3_files['frontend_hooks']:
    full_path = ROOT / file_path
    if full_path.exists():
        phase3_status['exists'].append(file_path)
        size = full_path.stat().st_size
        print(f"   ✅ {file_path} ({size:,} bytes)")
        
        hook_name = Path(file_path).stem
        used = False
        for tsx_file in (FRONTEND / 'app').rglob('*.tsx'):
            content = tsx_file.read_text(encoding='utf-8')
            if hook_name in content:
                used = True
                print(f"      ✅ Used in {tsx_file.relative_to(ROOT)}")
                break
        
        if not used:
            print(f"      ⚠️  Not used in any component")
    else:
        phase3_status['missing'].append(file_path)
        print(f"   ❌ {file_path} [MISSING]")

# ============================================================
# 4. ORPHAN FILES DETECTION
# ============================================================
print("\n" + "=" * 100)
print("🔍 ORPHAN FILES DETECTION")
print("=" * 100)

orphan_files = {
    'backend_services': [],
    'frontend_hooks': [],
    'frontend_components': [],
    'frontend_pages': []
}

# Check backend services
print("\n📂 Backend Services:")
services_dir = BACKEND / 'services'
if services_dir.exists():
    for py_file in services_dir.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
        
        rel_path = str(py_file.relative_to(ROOT))
        service_name = py_file.stem
        
        # Check if imported in any router
        imported = False
        for router in (BACKEND / 'modules').rglob('router.py'):
            content = router.read_text(encoding='utf-8-sig')
            if service_name in content:
                imported = True
                break
        
        if not imported:
            orphan_files['backend_services'].append(rel_path)
            print(f"   ⚠️  {rel_path} [NOT IMPORTED]")

# Check frontend hooks
print("\n🎨 Frontend Hooks:")
hooks_dir = FRONTEND / 'hooks'
if hooks_dir.exists():
    for ts_file in hooks_dir.rglob('*.ts'):
        if ts_file.name == '__init__.py':
            continue
        
        rel_path = str(ts_file.relative_to(ROOT))
        hook_name = ts_file.stem
        
        # Check if used in any component
        used = False
        for tsx_file in (FRONTEND / 'app').rglob('*.tsx'):
            content = tsx_file.read_text(encoding='utf-8')
            if hook_name in content:
                used = True
                break
        
        if not used:
            orphan_files['frontend_hooks'].append(rel_path)
            print(f"   ⚠️  {rel_path} [NOT USED]")

# Check frontend components
print("\n🧩 Frontend Components:")
components_dir = FRONTEND / 'components'
if components_dir.exists():
    for tsx_file in components_dir.rglob('*.tsx'):
        rel_path = str(tsx_file.relative_to(ROOT))
        component_name = tsx_file.stem
        
        # Check if imported in any page or component
        used = False
        for page_file in (FRONTEND / 'app').rglob('*.tsx'):
            content = page_file.read_text(encoding='utf-8')
            if component_name in content:
                used = True
                break
        
        if not used:
            orphan_files['frontend_components'].append(rel_path)
            print(f"   ⚠️  {rel_path} [NOT USED]")

# ============================================================
# 5. NAVIGATION LINKS CHECK
# ============================================================
print("\n" + "=" * 100)
print("🧭 NAVIGATION LINKS CHECK")
print("=" * 100)

# Find navbar files
navbar_files = []
for nav_file in FRONTEND.rglob('*Navbar*.tsx'):
    navbar_files.append(nav_file)
for nav_file in FRONTEND.rglob('*navbar*.tsx'):
    navbar_files.append(nav_file)

if navbar_files:
    navbar_file = navbar_files[0]
    content = navbar_file.read_text(encoding='utf-8')
    
    print(f"\n📄 Navbar file: {navbar_file.relative_to(ROOT)}")
    
    # Check for module links
    modules = [
        ('/academy', 'آکادمی'),
        ('/gis', 'GIS'),
        ('/weather', 'هواشناسی'),
        ('/drought', 'خشکسالی'),
        ('/iot', 'IoT'),
        ('/ecocoin', 'EcoCoin'),
        ('/mrv', 'MRV'),
        ('/soil-water', 'خاک و آب'),
    ]
    
    print("\n🔗 Module Links:")
    for path, name in modules:
        if path in content:
            print(f"   ✅ {name} ({path})")
        else:
            print(f"   ❌ {name} ({path}) [NOT IN NAVBAR]")
else:
    print("\n❌ Navbar file not found")

# ============================================================
# 6. PAGES WITHOUT NAVIGATION
# ============================================================
print("\n" + "=" * 100)
print("📄 PAGES WITHOUT NAVIGATION")
print("=" * 100)

pages_without_nav = []
app_dir = FRONTEND / 'app'

if app_dir.exists():
    for page_file in app_dir.rglob('page.tsx'):
        rel_path = page_file.relative_to(app_dir)
        page_path = '/' + str(rel_path.parent).replace('\\', '/')
        
        if page_path == '/.':
            page_path = '/'
        
        # Skip dynamic routes
        if '[' in page_path:
            continue
        
        # Check if in navbar
        in_navbar = False
        if navbar_files:
            content = navbar_files[0].read_text(encoding='utf-8')
            if page_path in content:
                in_navbar = True
        
        if not in_navbar and page_path != '/':
            pages_without_nav.append(page_path)
            print(f"   ⚠️  {page_path}")

# ============================================================
# 7. SUMMARY STATISTICS
# ============================================================
print("\n" + "=" * 100)
print("📊 SUMMARY STATISTICS")
print("=" * 100)

total_phase_files = (
    len(phase1_files['backend_services']) + len(phase1_files['frontend_hooks']) +
    len(phase2_files['backend_services']) + len(phase2_files['frontend_hooks']) +
    len(phase3_files['backend_services']) + len(phase3_files['frontend_hooks'])
)

total_exists = len(phase1_status['exists']) + len(phase2_status['exists']) + len(phase3_status['exists'])
total_missing = len(phase1_status['missing']) + len(phase2_status['missing']) + len(phase3_status['missing'])
total_imported = len(phase1_status['imported']) + len(phase2_status['imported']) + len(phase3_status['imported'])

total_orphans = (
    len(orphan_files['backend_services']) +
    len(orphan_files['frontend_hooks']) +
    len(orphan_files['frontend_components'])
)

print(f"\n📦 Phase Files:")
print(f"   Total expected: {total_phase_files}")
print(f"   ✅ Exists: {total_exists} ({total_exists/total_phase_files*100:.1f}%)")
print(f"   ❌ Missing: {total_missing} ({total_missing/total_phase_files*100:.1f}%)")
print(f"   ✅ Imported/Used: {total_imported}")

print(f"\n🔍 Orphan Files:")
print(f"   Backend services: {len(orphan_files['backend_services'])}")
print(f"   Frontend hooks: {len(orphan_files['frontend_hooks'])}")
print(f"   Frontend components: {len(orphan_files['frontend_components'])}")
print(f"   Total: {total_orphans}")

print(f"\n🧭 Navigation:")
print(f"   Pages without nav: {len(pages_without_nav)}")

# ============================================================
# 8. RECOMMENDATIONS
# ============================================================
print("\n" + "=" * 100)
print("💡 RECOMMENDATIONS")
print("=" * 100)

recommendations = []

if total_missing > 0:
    recommendations.append({
        'priority': 'CRITICAL',
        'issue': f'{total_missing} files missing',
        'action': 'Run phase implementation scripts'
    })

if len(orphan_files['backend_services']) > 0:
    recommendations.append({
        'priority': 'HIGH',
        'issue': f'{len(orphan_files["backend_services"])} backend services not imported',
        'action': 'Add imports to appropriate routers'
    })

if len(orphan_files['frontend_hooks']) > 0:
    recommendations.append({
        'priority': 'HIGH',
        'issue': f'{len(orphan_files["frontend_hooks"])} hooks not used',
        'action': 'Create components that use these hooks'
    })

if len(orphan_files['frontend_components']) > 0:
    recommendations.append({
        'priority': 'MEDIUM',
        'issue': f'{len(orphan_files["frontend_components"])} components not used',
        'action': 'Import in pages or delete if not needed'
    })

if len(pages_without_nav) > 0:
    recommendations.append({
        'priority': 'MEDIUM',
        'issue': f'{len(pages_without_nav)} pages not in navbar',
        'action': 'Add links to navbar or mark as internal pages'
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
# 9. FINAL STATUS
# ============================================================
print("\n" + "=" * 100)
print("🎯 FINAL STATUS")
print("=" * 100)

completion_rate = (total_exists / total_phase_files * 100) if total_phase_files > 0 else 0
integration_rate = (total_imported / total_exists * 100) if total_exists > 0 else 0

print(f"\n📊 Completion Rate: {completion_rate:.1f}%")
print(f"📊 Integration Rate: {integration_rate:.1f}%")

if completion_rate >= 95 and integration_rate >= 80:
    grade = "A+ 🏆"
    status = "EXCELLENT"
elif completion_rate >= 85 and integration_rate >= 70:
    grade = "A ✅"
    status = "VERY GOOD"
elif completion_rate >= 70 and integration_rate >= 60:
    grade = "B 👍"
    status = "GOOD"
elif completion_rate >= 50:
    grade = "C ⚠️"
    status = "NEEDS WORK"
else:
    grade = "D ❌"
    status = "CRITICAL"

print(f"📊 Grade: {grade}")
print(f"📊 Status: {status}")

print("\n" + "=" * 100)
print("✅ AUDIT COMPLETE")
print("=" * 100)