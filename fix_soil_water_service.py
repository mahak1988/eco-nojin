from pathlib import Path
import re

path = Path("api/modules/soil_water/service.py")
content = path.read_text(encoding='utf-8')

print(f"File size: {len(content)} bytes")

# Convert sync functions to async
# Find all db.execute() calls and add await
content = re.sub(
    r'(\s+)db\.execute\(',
    r'\1await db.execute(',
    content
)

# Find all function definitions and make them async
content = re.sub(
    r'^def (\w+)\(',
    r'async def \1(',
    content,
    flags=re.MULTILINE
)

# Write file
path.write_text(content, encoding='utf-8')
print(f"File updated ({len(content)} bytes)")
print("\nDone! Restart backend server.")