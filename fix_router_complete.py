from pathlib import Path
import re

path = Path("api/modules/soil_water/router.py")
content = path.read_text(encoding='utf-8')

print(f"File size: {len(content)} bytes")

# Step 1: Convert all endpoint functions to async
# Pattern: @router.xxx(...) \n def function_name(
content = re.sub(
    r'(@router\.(?:get|post|put|delete|patch)\([^\)]*\)\s*\n)def\s+(\w+)\s*\(',
    r'\1async def \2(',
    content
)

# Step 2: Ensure all service calls have await
# Pattern: soil_service.function( without await
content = re.sub(
    r'(?<!await\s)(soil_service\.\w+\()',
    r'await \1',
    content
)

# Also handle: water_service, erosion_service
content = re.sub(
    r'(?<!await\s)(water_service\.\w+\()',
    r'await \1',
    content
)

content = re.sub(
    r'(?<!await\s)(erosion_service\.\w+\()',
    r'await \1',
    content
)

# Step 3: Ensure db.execute has await
content = re.sub(
    r'(?<!await\s)(db\.execute\()',
    r'await \1',
    content
)

# Write file
path.write_text(content, encoding='utf-8')
print(f"File updated ({len(content)} bytes)")

# Verify
verify = path.read_text(encoding='utf-8')
async_funcs = len(re.findall(r'async def', verify))
await_calls = len(re.findall(r'await', verify))
print(f"\nVerification:")
print(f"  - async functions: {async_funcs}")
print(f"  - await calls: {await_calls}")

print("\nDone! Restart backend server.")