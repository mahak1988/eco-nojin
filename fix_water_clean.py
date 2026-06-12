from pathlib import Path
import re

path = Path("api/modules/water/models.py")
old_content = path.read_text(encoding='utf-8')

print(f"Old file size: {len(old_content)} bytes")

water_balance_match = re.search(
    r'class WaterBalance\(Base\):.*?(?=\nclass |\Z)',
    old_content,
    re.DOTALL
)

water_balance_code = ""
if water_balance_match:
    water_balance_code = water_balance_match.group(0)
    print(f"WaterBalance class found ({len(water_balance_code)} chars)")
else:
    print("WaterBalance class not found")

new_content = '''"""
Water Module Models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from api.core.database import Base


class Scenario(Base):
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


''' + water_balance_code

path.write_text(new_content, encoding='utf-8')
print(f"New file written ({len(new_content)} bytes)")

db_paths = [Path("econojin.db"), Path("api/econojin.db")]
for db_path in db_paths:
    if db_path.exists():
        try:
            db_path.unlink()
            print(f"Deleted: {db_path}")
        except Exception as e:
            print(f"Cannot delete {db_path}: {e}")
            print("Stop backend server first (Ctrl+C)")

print("\nDone! Now:")
print("1. Stop backend server (Ctrl+C)")
print("2. Delete database: Remove-Item 'econojin.db' -Force")
print("3. Restart: uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")