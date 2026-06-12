from pathlib import Path

# ============================================================================
# 1. Delete water/models.py (duplicate definitions)
# ============================================================================
water_models = Path("api/modules/water/models.py")
if water_models.exists():
    water_models.unlink()
    print(f"🗑️ Deleted: {water_models}")
else:
    print(f"ℹ️  Not found: {water_models}")


# ============================================================================
# 2. Fix all_models.py - remove water import
# ============================================================================
all_models = Path("api/modules/all_models.py")
content = all_models.read_text(encoding='utf-8')

# Remove water import
content = content.replace(
    'from api.modules.water import models as water_models\n',
    ''
)
content = content.replace(
    '"water_models",\n',
    ''
)

all_models.write_text(content, encoding='utf-8')
print(f"✅ Updated: {all_models}")


# ============================================================================
# 3. Fix soil_water/models.py - add farmer relationship
# ============================================================================
soil_water_models = Path("api/modules/soil_water/models.py")
content = soil_water_models.read_text(encoding='utf-8')

# Add farmer relationship to SoilWaterAnalysis
if 'farmer = relationship("Farmer"' not in content:
    # Find SoilWaterAnalysis class and add relationship
    content = content.replace(
        'updated_at = Column(DateTime(timezone=True), onupdate=func.now())\n\n\n# ============================================================================\n# Irrigation Schedule Model',
        'updated_at = Column(DateTime(timezone=True), onupdate=func.now())\n    \n    farmer = relationship("Farmer", back_populates="soil_water_analyses")\n\n\n# ============================================================================\n# Irrigation Schedule Model'
    )
    print("✅ Added farmer relationship to SoilWaterAnalysis")
else:
    print("ℹ️  farmer relationship already exists")

soil_water_models.write_text(content, encoding='utf-8')
print(f"✅ Updated: {soil_water_models}")


# ============================================================================
# 4. Fix farmer/models.py - add soil_water_analyses relationship
# ============================================================================
farmer_models = Path("api/modules/farmer/models.py")
content = farmer_models.read_text(encoding='utf-8')

# Add soil_water_analyses relationship
if 'soil_water_analyses = relationship' not in content:
    # Add relationship import if missing
    if 'from sqlalchemy.orm import relationship' not in content:
        content = content.replace(
            'from sqlalchemy import',
            'from sqlalchemy.orm import relationship\nfrom sqlalchemy import'
        )
        print("✅ Added relationship import")
    
    # Find Farmer class and add relationship
    lines = content.split('\n')
    insert_idx = -1
    
    for i, line in enumerate(lines):
        if 'class Farmer(Base):' in line or 'class Farmer(' in line:
            # Find end of class
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                    insert_idx = j
                    break
                if j == len(lines) - 1:
                    insert_idx = j + 1
            break
    
    if insert_idx > 0:
        relationship_line = '    soil_water_analyses = relationship("SoilWaterAnalysis", back_populates="farmer", lazy="selectin")'
        lines.insert(insert_idx, relationship_line)
        content = '\n'.join(lines)
        print("✅ Added soil_water_analyses relationship to Farmer")
    else:
        print("⚠️  Could not find Farmer class end")

farmer_models.write_text(content, encoding='utf-8')
print(f"✅ Updated: {farmer_models}")


# ============================================================================
# 5. Delete database
# ============================================================================
for db in [Path("econojin.db"), Path("api/econojin.db")]:
    if db.exists():
        try:
            db.unlink()
            print(f"🗑️ Deleted: {db}")
        except Exception as e:
            print(f"⚠️ Cannot delete {db}: {e}")


print("\n" + "=" * 70)
print("✅ All fixes applied!")
print("=" * 70)
print("\nNext steps:")
print("1. Stop backend server (Ctrl+C)")
print("2. Remove-Item 'econojin.db' -Force")
print("3. uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")