from pathlib import Path
import re

# Fix maintenance router - remove problematic import
router_path = Path('api/modules/maintenance/router.py')
if router_path.exists():
    content = router_path.read_text(encoding='utf-8')
    # Remove the problematic line
    content = re.sub(r'from api\.services\.early_warning_engine import.*\n', '', content)
    router_path.write_text(content, encoding='utf-8')
    print("✅ Removed early_warning_engine import from maintenance router")

# Fix soil_water router - remove problematic imports
router_path = Path('api/modules/soil_water/router.py')
if router_path.exists():
    content = router_path.read_text(encoding='utf-8')
    content = re.sub(r'from api\.services\.rothc_full import.*\n', '', content)
    content = re.sub(r'from api\.services\.soil_water_calculator import.*\n', '', content)
    router_path.write_text(content, encoding='utf-8')
    print("✅ Removed problematic imports from soil_water router")

print("\n🚀 Now try: uvicorn api.main:app --reload --port 8000")