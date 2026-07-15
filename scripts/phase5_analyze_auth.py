#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Phase 5: Authentication Backend Analysis
=====================================================
بررسی endpoints موجود و ناقص بک‌اند Authentication
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Set

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = PROJECT_ROOT / "apps"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    DIM = '\033[2m'
    BOLD = '\033[1m'
    END = '\033[0m'

def cprint(msg: str, color: str = Colors.END):
    print(f"{color}{msg}{Colors.END}")

def analyze_router(file_path: Path) -> Dict[str, List[str]]:
    """تحلیل router و استخراج endpoints"""
    
    endpoints = {
        'get': [],
        'post': [],
        'put': [],
        'delete': [],
        'patch': [],
    }
    
    if not file_path.exists():
        return endpoints
    
    content = file_path.read_text(encoding="utf-8")
    
    # الگوهای FastAPI decorators
    patterns = {
        'get': r'@router\.get\(["\']([^"\']+)["\']',
        'post': r'@router\.post\(["\']([^"\']+)["\']',
        'put': r'@router\.put\(["\']([^"\']+)["\']',
        'delete': r'@router\.delete\(["\']([^"\']+)["\']',
        'patch': r'@router\.patch\(["\']([^"\']+)["\']',
    }
    
    for method, pattern in patterns.items():
        matches = re.findall(pattern, content)
        endpoints[method] = matches
    
    return endpoints

def analyze_auth_requirements() -> Dict[str, List[str]]:
    """تحلیل نیازمندی‌های Authentication"""
    
    # Endpoints مورد نیاز فرانت‌اند
    required = {
        'login': '/auth/login',
        'register': '/auth/register',
        'logout': '/auth/logout',
        'me': '/auth/me',
        'refresh': '/auth/refresh',
        'forgot_password': '/auth/forgot-password',
        'reset_password': '/auth/reset-password',
    }
    
    return required

def main():
    cprint("\n" + "=" * 70, Colors.BOLD)
    cprint("🔍 Phase 5: Authentication Backend Analysis", Colors.BOLD)
    cprint("=" * 70, Colors.BOLD)
    
    # Step 1: بررسی router های موجود
    cprint("\n📝 Step 1: Checking existing routers...", Colors.BLUE)
    
    router_files = [
        ("users", APPS_DIR / "users" / "router.py"),
        ("ai_agents", APPS_DIR / "ai_agents" / "router.py"),
    ]
    
    existing_endpoints = {}
    
    for module, router_path in router_files:
        if router_path.exists():
            endpoints = analyze_router(router_path)
            total = sum(len(v) for v in endpoints.values())
            cprint(f"   ✅ {module}: {total} endpoints found", Colors.GREEN)
            existing_endpoints[module] = endpoints
        else:
            cprint(f"   ❌ {module}: router not found", Colors.RED)
    
    # Step 2: تحلیل endpoints موجود
    cprint("\n📝 Step 2: Analyzing existing endpoints...", Colors.BLUE)
    
    if 'users' in existing_endpoints:
        user_endpoints = existing_endpoints['users']
        
        cprint("\n   📋 User Router Endpoints:", Colors.CYAN)
        for method, paths in user_endpoints.items():
            if paths:
                cprint(f"      {method.upper()}: {', '.join(paths)}", Colors.DIM)
    
    # Step 3: بررسی نیازمندی‌ها
    cprint("\n📝 Step 3: Checking authentication requirements...", Colors.BLUE)
    
    required = analyze_auth_requirements()
    
    cprint("\n   🎯 Required Auth Endpoints:", Colors.CYAN)
    for name, path in required.items():
        cprint(f"      • {name}: {path}", Colors.DIM)
    
    # Step 4: شناسایی شکاف‌ها
    cprint("\n📝 Step 4: Identifying gaps...", Colors.BLUE)
    
    # بررسی اینکه آیا auth router وجود دارد
    auth_router = APPS_DIR / "users" / "auth_router.py"
    auth_router_alt = APPS_DIR / "auth" / "router.py"
    
    if auth_router.exists() or auth_router_alt.exists():
        cprint("   ✅ Auth router found", Colors.GREEN)
    else:
        cprint("   ❌ Auth router not found - needs to be created", Colors.RED)
    
    # Step 5: تولید گزارش
    cprint("\n" + "=" * 70, Colors.BOLD)
    cprint("📊 Analysis Report", Colors.BOLD)
    cprint("=" * 70, Colors.BOLD)
    
    cprint("\n✅ موجود:", Colors.GREEN)
    if 'users' in existing_endpoints:
        for method, paths in existing_endpoints['users'].items():
            if paths:
                cprint(f"   • {method.upper()}: {len(paths)} endpoints", Colors.DIM)
    
    cprint("\n❌ ناقص:", Colors.RED)
    cprint("   • Auth router (login, register, logout, me, refresh)", Colors.DIM)
    
    cprint("\n📌 Next steps:", Colors.BLUE)
    cprint("   1. Create/Register auth_router.py with required endpoints", Colors.DIM)
    cprint("   2. Test endpoints with curl/Postman", Colors.DIM)
    cprint("   3. Connect frontend to backend", Colors.DIM)


if __name__ == "__main__":
    main()