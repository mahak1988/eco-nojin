from pathlib import Path
import re

path = Path("api/modules/water/models.py")
content = path.read_text(encoding='utf-8')

print(f"File size: {len(content)} bytes")
print("\nFirst 500 chars:")
print(content[:500])
print("\n" + "=" * 70)

# Check if Scenario already exists
if 'class Scenario' in content:
    print("Scenario class already exists")
else:
    print("Adding Scenario class...")
    
    # Find the first import line
    lines = content.split('\n')
    
    # Find where to insert Scenario class (after all imports, before first class)
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('class ') and 'Base' in line:
            insert_idx = i
            break
    
    # Scenario class code
    scenario_code = '''
class Scenario(Base):
    """Scenario model for water analysis"""
    __tablename__ = "scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scenario_type = Column(String(100), nullable=True)
    parameters = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    water_balances = relationship("WaterBalance", back_populates="scenario")

'''
    
    # Insert Scenario class
    lines.insert(insert_idx, scenario_code)
    content = '\n'.join(lines)

# Fix imports - ensure all needed types are imported
# Find the sqlalchemy import line
import_pattern = r'from sqlalchemy import ([^\n]+)'
match = re.search(import_pattern, content)

if match:
    current_imports = match.group(1)
    print(f"\nCurrent imports: {current_imports}")
    
    # Add missing imports
    needed = ['Column', 'Integer', 'String', 'Float', 'DateTime', 'Text', 
              'Boolean', 'JSON', 'ForeignKey', 'Date']
    
    missing = [n for n in needed if n not in current_imports]
    
    if missing:
        print(f"Missing imports: {missing}")
        # Add missing imports
        new_imports = current_imports.rstrip()
        for m in missing:
            if m not in new_imports:
                new_imports += f', {m}'
        
        content = content.replace(
            f'from sqlalchemy import {current_imports}',
            f'from sqlalchemy import {new_imports}'
        )
        print(f"New imports: {new_imports}")
    else:
        print("All imports present")
else:
    print("WARNING: Could not find sqlalchemy import line")

# Write file
path.write_text(content, encoding='utf-8')
print(f"\nFile updated ({len(content)} bytes)")

# Delete database
for db in [Path("econojin.db"), Path("api/econojin.db")]:
    if db.exists():
        try:
            db.unlink()
            print(f"Deleted: {db}")
        except Exception as e:
            print(f"Cannot delete {db}: {e}")

print("\n" + "=" * 70)
print("DONE!")
print("\nNext steps:")
print("1. Stop backend (Ctrl+C)")
print("2. Remove-Item 'econojin.db' -Force")
print("3. uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")