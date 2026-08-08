#!/usr/bin/env python3
"""
Generate and insert seed data for main application tables.
This script connects to the database and inserts default/core records.
"""

import asyncio
import json
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from apps.shared_core.config import get_settings
from apps.users.models import User
from apps.farms.models import Farm
from apps.shared_core.security import get_password_hash

settings = get_settings()

# Define some sample data
SEED_USERS = [
    {
        "email": "admin@econojin.test",
        "full_name": "Admin User",
        "role": "admin",
        "is_superuser": True,
        "password": "default_admin_password" # Should be changed immediately after seeding
    },
    {
        "email": "farmer1@econojin.test",
        "full_name": "John Doe",
        "role": "farmer",
        "is_superuser": False,
        "password": "default_farmer_password"
    }
]

SEED_FARMS = [
    {
        "name": "Demo Farm 1",
        "description": "A sample farm for demonstration purposes.",
        "owner_id": 2, # Assuming farmer1 owns this
        "region": "Test Region A",
        "area_ha": 50.0,
        "latitude": 35.6895,
        "longitude": 51.3890
    }
]


async def insert_seed_data():
    """Connects to the database and inserts seed data."""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("Inserting seed data...")

        # Insert Users
        for user_data in SEED_USERS:
            existing_user = await session.get(User, user_data["email"]) # This won't work, need to query by email
            from sqlalchemy import select
            result = await session.execute(select(User).filter(User.email == user_data["email"]))
            existing_user = result.scalars().first()

            if not existing_user:
                user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
                new_user = User(**user_data)
                session.add(new_user)
                print(f"  Added user: {user_data['email']}")

        # Insert Farms
        for farm_data in SEED_FARMS:
            # Simple check to avoid duplicates based on name (not ideal for production)
            from sqlalchemy import select
            result = await session.execute(select(Farm).filter(Farm.name == farm_data["name"]))
            existing_farm = result.scalars().first()

            if not existing_farm:
                new_farm = Farm(**farm_data)
                session.add(new_farm)
                print(f"  Added farm: {farm_data['name']}")

        await session.commit()
        print("Seed data insertion complete.")


if __name__ == "__main__":
    asyncio.run(insert_seed_data())