"""Reset database - delete and recreate"""

import os
import sys
import asyncio

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())


async def reset_db():
    db_path = "data/econojin.db"
    
    print("=" * 60)
    print("Reset Database")
    print("=" * 60)
    print()
    
    # Delete old database
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"[1/2] Deleted: {db_path}")
    else:
        print(f"[1/2] No database to delete")
    
    # Recreate tables
    from app.core.database import init_db
    await init_db()
    print(f"[2/2] Database recreated")
    print()
    print("=" * 60)
    print("SUCCESS: Database reset complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(reset_db())
