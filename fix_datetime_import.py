from pathlib import Path

path = Path("api/modules/soil_water/models.py")
content = path.read_text(encoding='utf-8')

print(f"File size: {len(content)} bytes")

# Fix 1: Add datetime import if missing
if 'from datetime import' not in content:
    # Add import at the top after other imports
    content = content.replace(
        'from sqlalchemy import',
        'from datetime import datetime, date\nfrom sqlalchemy import'
    )
    print("✅ Added: from datetime import datetime, date")
else:
    print("✅ datetime import already exists")

# Fix 2: Replace datetime.utcnow with func.now() (SQLAlchemy standard)
content = content.replace(
    'default=datetime.utcnow',
    'server_default=func.now()'
)
print("✅ Replaced: datetime.utcnow → func.now()")

# Write file
path.write_text(content, encoding='utf-8')
print(f"\n✅ File updated ({len(content)} bytes)")

# Delete database
for db in [Path("econojin.db"), Path("api/econojin.db")]:
    if db.exists():
        try:
            db.unlink()
            print(f"🗑️ Deleted: {db}")
        except Exception as e:
            print(f"⚠️ Cannot delete {db}: {e}")

print("\nDone! Restart backend server.")