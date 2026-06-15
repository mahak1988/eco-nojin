"""Seed script to create initial admin user"""

import sys
import os
import asyncio

# Add parent directory to path so 'app' can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.core.database import AsyncSessionLocal, init_db
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash


async def seed_admin():
    """Create initial admin user"""
    await init_db()
    
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(
            select(User).where(User.email == "admin@econojin.com")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("WARNING: Admin user already exists")
            print(f"   ID: {existing.id}")
            print(f"   Email: {existing.email}")
            return
        
        admin = User(
            email="admin@econojin.com",
            hashed_password=get_password_hash("admin123456"),
            full_name="Super Admin",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            trust_score=100.0,
            is_verified=True,
            location="Global",
            bio="System administrator",
        )
        
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        
        print("SUCCESS: Admin user created!")
        print(f"   ID: {admin.id}")
        print(f"   Email: admin@econojin.com")
        print(f"   Password: admin123456")
        print(f"   Role: {admin.role.value}")


if __name__ == "__main__":
    asyncio.run(seed_admin())
