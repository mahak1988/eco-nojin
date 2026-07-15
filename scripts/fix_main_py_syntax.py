#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Fix main.py Syntax and Register Auth Router
=======================================================
این اسکریپت خطای SyntaxError را رفع کرده و auth_router را به درستی ثبت می‌کند.
"""

import re
from pathlib import Path
import shutil

MAIN_PY = Path("apps/main.py")

def main():
    print("\n" + "=" * 70)
    print("🔧 Fixing main.py Syntax & Registering Auth Router")
    print("=" * 70)
    
    if not MAIN_PY.exists():
        print(f"\n❌ main.py not found at: {MAIN_PY}")
        return
    
    # Backup
    backup_path = MAIN_PY.with_suffix(".py.backup_fix")
    try:
        shutil.copy2(MAIN_PY, backup_path)
        print(f"\n💾 Backup created: {backup_path.name}")
    except Exception as e:
        print(f"\n⚠️  Backup failed: {e}")
    
    content = MAIN_PY.read_text(encoding="utf-8")
    
    # Step 1: Remove the misplaced import (if it exists anywhere incorrectly)
    content = re.sub(r'\n\s*from apps\.users\.auth_router import router as auth_router\s*\n', '\n', content)
    
    # Step 2: Add import at the top (after users_router import)
    if "from apps.users.auth_router import router as auth_router" not in content:
        content = content.replace(
            "from apps.users.router import router as users_router",
            "from apps.users.router import router as users_router\nfrom apps.users.auth_router import router as auth_router"
        )
        print("\n✅ Step 1: Import added at the top of the file.")
    else:
        print("\n⏩ Step 1: Import already exists in the correct place.")
    
    # Step 3: Add router registration safely
    if "app.include_router(auth_router" not in content:
        # Try to find the users_router registration
        pattern = r'(app\.include_router\(users_router[^)]+\))'
        match = re.search(pattern, content)
        
        if match:
            insert_pos = match.end()
            new_router_line = '\n    app.include_router(auth_router, prefix="/api/v1", tags=["🔐 Authentication"])'
            content = content[:insert_pos] + new_router_line + content[insert_pos:]
            print("✅ Step 2: Router registered next to users_router.")
        else:
            # Fallback: Add it just before the main execution block
            content = content.replace(
                'if __name__ == "__main__":',
                'app.include_router(auth_router, prefix="/api/v1", tags=["🔐 Authentication"])\n\nif __name__ == "__main__":'
            )
            print("✅ Step 2: Router registered (Fallback method).")
    else:
        print("\n⏩ Step 2: Router already registered.")
    
    # Step 4: Write back
    try:
        MAIN_PY.write_text(content, encoding="utf-8")
        print("\n✅ main.py updated and syntax fixed successfully!")
    except Exception as e:
        print(f"\n❌ Failed to write main.py: {e}")
        return
    
    print("\n" + "=" * 70)
    print("✅ Fix completed!")
    print("=" * 70)
    
    print("\n📌 Next steps:")
    print("   1. Run: python apps/main.py")
    print("   2. Look for: ✅ auth: روتر بارگذاری شد")
    print("   3. Open: http://localhost:8000/docs")


if __name__ == "__main__":
    main()