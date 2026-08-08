#!/usr/bin/env python3
# scripts/seed_demo.py — Phase 2 Demo Seed Data
# Creates demo user, courses, accounting entries, and sample simulation runs.

import sys

sys.path.insert(0, ".")

import asyncio

from apps.shared_core.database.session import get_db_session, init_db
from apps.shared_core.security import get_password_hash
from apps.users.models import User


async def seed():
    print("[seed] Initializing database...")
    await init_db()

    async with get_db_session() as db:
        # Demo user
        demo = User(
            email="demo@econojin.com",
            full_name="Demo Farmer",
            hashed_password=get_password_hash("demo123456"),
            role="farmer",
            is_active=True,
            is_superuser=False,
        )
        db.add(demo)

        # Admin user
        admin = User(
            email="admin@econojin.com",
            full_name="Admin",
            hashed_password=get_password_hash("admin123456"),
            role="admin",
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)

        await db.commit()

    print("[seed] Done. Demo users created:")
    print("  demo@econojin.com / demo123456 (farmer)")
    print("  admin@econojin.com / admin123456 (admin)")


if __name__ == "__main__":
    asyncio.run(seed())
