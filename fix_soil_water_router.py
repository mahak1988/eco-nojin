from pathlib import Path
import re

path = Path("api/modules/soil_water/router.py")
content = path.read_text(encoding='utf-8')

print(f"File size: {len(content)} bytes")

# Add await to all service calls
# Pattern: service.function_name(
content = re.sub(
    r'(\s+)((?:soil_service|water_service|erosion_service)\.\w+)\(',
    r'\1await \2(',
    content
)

# Also handle: total, items = service.function(
content = re.sub(
    r'(\w+,\s*\w+)\s*=\s*((?:soil_service|water_service|erosion_service)\.\w+)\(',
    r'\1 = await \2(',
    content
)

# Write file
path.write_text(content, encoding='utf-8')
print(f"File updated ({len(content)} bytes)")
print("\nDone! Restart backend server.")