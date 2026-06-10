"""
🔧 اصلاح کامل و هوشمند تمام Import ها
تشخیص خودکار نام‌های export شده و اصلاح import statements
"""
from pathlib import Path
import re
import ast
import sys

print("=" * 100)
print("🔧 COMPLETE IMPORT FIX - Smart Auto-Detection")
print("=" * 100)

ROOT = Path('.')
BACKEND = ROOT / 'api'

def get_exported_names(file_path: Path) -> dict:
    """استخراج تمام نام‌های export شده از فایل پایتون"""
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        exports = {
            'classes': [],
            'functions': [],
            'variables': [],
            'instances': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                exports['classes'].append(node.name)
            elif isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):
                    exports['functions'].append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        exports['variables'].append(target.id)
                        # Check if it's an instance (lowercase or ends with _instance)
                        if target.id[0].islower() or '_instance' in target.id:
                            exports['instances'].append(target.id)
        
        return exports
    except Exception as e:
        print(f"   ⚠️  Error parsing {file_path}: {e}")
        return {'classes': [], 'functions': [], 'variables': [], 'instances': []}

# ============================================================
# 1. ANALYZE ALL ORPHAN SERVICES
# ============================================================
print("\n🔍 1. Analyzing All Orphan Services...")

orphan_services = {
    'early_warning_engine': 'api/services/early_warning_engine.py',
    'rothc_full': 'api/services/rothc_full.py',
    'soil_water_calculator': 'api/services/soil_water_calculator.py',
    'ai_service': 'api/services/ai/ai_service.py',
}

service_exports = {}
for name, path in orphan_services.items():
    full_path = ROOT / path
    if full_path.exists():
        exports = get_exported_names(full_path)
        service_exports[name] = exports
        print(f"\n📄 {name}")
        print(f"   Classes: {exports['classes']}")
        print(f"   Functions: {exports['functions']}")
        print(f"   Variables: {exports['variables']}")
        print(f"   Instances: {exports['instances']}")
    else:
        print(f"\n❌ {name} [NOT FOUND]")

# ============================================================
# 2. FIX MAINTENANCE ROUTER
# ============================================================
print("\n\n🔧 2. Fixing Maintenance Router...")

maintenance_router = BACKEND / 'modules' / 'maintenance' / 'router.py'
if maintenance_router.exists():
    content = maintenance_router.read_text(encoding='utf-8-sig')
    
    # Remove old incorrect imports
    content = re.sub(r'from api\.services\.early_warning_engine import.*\n', '', content)
    
    # Add correct import
    if 'early_warning_engine' in service_exports:
        exports = service_exports['early_warning_engine']
        
        # Priority: instance > class > function
        import_name = None
        if exports['instances']:
            import_name = exports['instances'][0]
        elif exports['classes']:
            import_name = exports['classes'][0]
        elif exports['functions']:
            import_name = exports['functions'][0]
        
        if import_name:
            content = f'from api.services.early_warning_engine import {import_name}\n' + content
            print(f"   ✅ Imported: {import_name}")
    
    maintenance_router.write_text(content, encoding='utf-8')

# ============================================================
# 3. FIX SOIL_WATER ROUTER
# ============================================================
print("\n🔧 3. Fixing Soil-Water Router...")

soil_water_router = BACKEND / 'modules' / 'soil_water' / 'router.py'
if soil_water_router.exists():
    content = soil_water_router.read_text(encoding='utf-8-sig')
    
    # Remove old incorrect imports
    content = re.sub(r'from api\.services\.rothc_full import.*\n', '', content)
    content = re.sub(r'from api\.services\.soil_water_calculator import.*\n', '', content)
    
    imports_to_add = []
    
    # Fix rothc_full
    if 'rothc_full' in service_exports:
        exports = service_exports['rothc_full']
        import_name = None
        if exports['instances']:
            import_name = exports['instances'][0]
        elif exports['classes']:
            import_name = exports['classes'][0]
        elif exports['functions']:
            import_name = exports['functions'][0]
        
        if import_name:
            imports_to_add.append(f'from api.services.rothc_full import {import_name}')
            print(f"   ✅ rothc_full: {import_name}")
    
    # Fix soil_water_calculator
    if 'soil_water_calculator' in service_exports:
        exports = service_exports['soil_water_calculator']
        import_name = None
        if exports['instances']:
            import_name = exports['instances'][0]
        elif exports['classes']:
            import_name = exports['classes'][0]
        elif exports['functions']:
            import_name = exports['functions'][0]
        
        if import_name:
            imports_to_add.append(f'from api.services.soil_water_calculator import {import_name}')
            print(f"   ✅ soil_water_calculator: {import_name}")
    
    if imports_to_add:
        content = '\n'.join(imports_to_add) + '\n' + content
    
    soil_water_router.write_text(content, encoding='utf-8')

# ============================================================
# 4. FIX AI ROUTER
# ============================================================
print("\n🔧 4. Fixing AI Router...")

ai_router = BACKEND / 'modules' / 'ai' / 'router.py'
if ai_router.exists():
    content = ai_router.read_text(encoding='utf-8-sig')
    
    # Remove old incorrect imports
    content = re.sub(r'from api\.services\.ai\.ai_service import.*\n', '', content)
    
    # Add correct import
    if 'ai_service' in service_exports:
        exports = service_exports['ai_service']
        import_name = None
        
        # Look for service instance or class
        for inst in exports['instances']:
            if 'service' in inst.lower() or 'ai' in inst.lower():
                import_name = inst
                break
        
        if not import_name and exports['classes']:
            for cls in exports['classes']:
                if 'service' in cls.lower() or 'ai' in cls.lower():
                    import_name = cls
                    break
        
        if not import_name and exports['instances']:
            import_name = exports['instances'][0]
        elif not import_name and exports['classes']:
            import_name = exports['classes'][0]
        
        if import_name:
            content = f'from api.services.ai.ai_service import {import_name}\n' + content
            print(f"   ✅ AI service: {import_name}")
    
    ai_router.write_text(content, encoding='utf-8')

# ============================================================
# 5. CLEAN MAIN.PY
# ============================================================
print("\n🔧 5. Cleaning main.py...")

main_path = BACKEND / 'main.py'
if main_path.exists():
    content = main_path.read_text(encoding='utf-8-sig')
    
    # Remove duplicate imports
    lines = content.split('\n')
    seen_imports = set()
    clean_lines = []
    
    for line in lines:
        if line.strip().startswith('from api.modules') and 'router' in line:
            if line in seen_imports:
                continue
            seen_imports.add(line)
        clean_lines.append(line)
    
    content = '\n'.join(clean_lines)
    main_path.write_text(content, encoding='utf-8')
    print("   ✅ Cleaned duplicates")

# ============================================================
# 6. TEST IMPORT
# ============================================================
print("\n🧪 6. Testing imports...")

sys.path.insert(0, str(ROOT))

try:
    import importlib
    if 'api.main' in sys.modules:
        del sys.modules['api.main']
    
    import api.main
    print("   ✅ api.main imports successfully!")
    print("   ✅ Backend is ready to start!")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    print("\n💡 Error details:")
    import traceback
    traceback.print_exc()

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("✅ IMPORT FIX COMPLETE")
print("=" * 100)

print("""
🚀 Next Steps:

1. Start backend:
   uvicorn api.main:app --reload --port 8000

2. Start frontend (in another terminal):
   cd apps/web
   npx next dev -p 3001

3. Test all modules:
   - http://localhost:3001/academy
   - http://localhost:3001/gis
   - http://localhost:3001/weather
   - http://localhost:3001/drought
   - http://localhost:3001/iot
   - http://localhost:3001/ecocoin
   - http://localhost:3001/mrv
   - http://localhost:3001/soil-water

4. Run audit again:
   python audit_phases_implementation.py
""")