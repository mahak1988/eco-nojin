#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Phase 5: Register Auth Router in main.py
=====================================================
"""

from pathlib import Path

MAIN_PY = Path("apps/main.py")

def main():
    print("\n" + "=" * 70)
    print("🔧 Registering Auth Router in main.py")
    print("=" * 70)
    
    if not MAIN_PY.exists():
        print(f"\n❌ main.py not found at: {MAIN_PY}")
        return
    
    # Backup
    backup_path = MAIN_PY.with_suffix(".py.backup_auth")
    try:
        import shutil
        shutil.copy2(MAIN_PY, backup_path)
        print(f"\n💾 Backup created: {backup_path.name}")
    except Exception as e:
        print(f"\n⚠️  Backup failed: {e}")
    
    content = MAIN_PY.read_text(encoding="utf-8")
    
    # Step 1: Add import
    print("\n📝 Step 1: Adding import...")
    
    if "from apps.users.auth_router import router as auth_router" in content:
        print("   ⏩ Import already exists")
    else:
        # پیدا کردن خط import users_router
        if "from apps.users.router import router as users_router" in content:
            content = content.replace(
                "from apps.users.router import router as users_router",
                "from apps.users.router import router as users_router\nfrom apps.users.auth_router import router as auth_router"
            )
            print("   ✅ Import added")
        else:
            print("   ⚠️  Could not find users_router import")
            print("   📌 Manual fix required")
    
    # Step 2: Register router
    print("\n📝 Step 2: Registering router...")
    
    if "app.include_router(auth_router)" in content:
        print("   ⏩ Router already registered")
    else:
        # پیدا کردن خط registration users_router
        if 'app.include_router(users_router' in content:
            # اضافه کردن بعد از users_router
            content = content.replace(
                'app.include_router(users_router, prefix="/api/v1/users", tags=["👤 Users"])',
                'app.include_router(users_router, prefix="/api/v1/users", tags=["👤 Users"])\n    app.include_router(auth_router, prefix="/api/v1", tags=["🔐 Authentication"])'
            )
            print("   ✅ Router registered")
        else:
            print("   ⚠️  Could not find users_router registration")
            print("   📌 Manual fix required")
    
    # Step 3: Write back
    try:
        MAIN_PY.write_text(content, encoding="utf-8")
        print(f"\n✅ main.py updated successfully")
    except Exception as e:
        print(f"\n❌ Failed to write main.py: {e}")
        return
    
    print("\n" + "=" * 70)
    print("✅ Auth Router registered!")
    print("=" * 70)
    
    print("\n📌 Next steps:")
    print("   1. Restart backend: Ctrl+C, then python apps/main.py")
    print("   2. Check logs for: ✅ auth: روتر بارگذاری شد")
    print("   3. Test with curl:")
    print("      curl http://localhost:8000/docs")


if __name__ == "__main__":
    main()