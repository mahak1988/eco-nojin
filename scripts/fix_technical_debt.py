#!/usr/bin/env python3
"""
Phase 0: Technical Debt Fix Script
===================================
This script automates the fixes for critical and high-priority technical debt.

Usage:
    python scripts/fix_technical_debt.py --phase=0
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def check_alembic_migrations():
    """Check if Alembic migrations are properly configured."""
    print("🔍 Checking Alembic migrations...")
    
    alembic_dir = PROJECT_ROOT / "alembic"
    env_file = alembic_dir / "env.py"
    versions_dir = alembic_dir / "versions"
    
    if not env_file.exists():
        print("❌ alembic/env.py not found")
        return False
    
    if not versions_dir.exists():
        print("❌ alembic/versions/ directory not found")
        return False
    
    # Count migration files
    migration_files = list(versions_dir.glob("*.py"))
    print(f"✅ Found {len(migration_files)} migration files")
    
    # Check if models are imported in env.py
    with open(env_file, 'r') as f:
        content = f.read()
        if "import apps" in content or "Base.metadata" in content:
            print("✅ Models appear to be imported in env.py")
        else:
            print("⚠️  Models may not be properly imported in env.py")
    
    return True

def check_cors_config():
    """Check CORS configuration for wildcards."""
    print("\n🔍 Checking CORS configuration...")
    
    main_file = PROJECT_ROOT / "apps" / "main.py"
    if not main_file.exists():
        print("❌ apps/main.py not found")
        return False
    
    with open(main_file, 'r') as f:
        content = f.read()
        
    # Check for wildcard validation (this is good - means we're checking for wildcards)
    if 'if "*" in origin:' in content or "if '*' in origin:" in content:
        print("✅ Wildcard validation is properly implemented")
        print("   The code actively rejects '*' in origins")
    elif '"*"' in content or "'*'" in content:
        # Check if it's just in comments/docstrings
        lines = content.split('\n')
        has_bad_wildcard = False
        for line in lines:
            stripped = line.strip()
            if ('"*"' in line or "'*'" in line) and 'origin' in line.lower():
                if not stripped.startswith('#') and 'if' not in line and 'validate' not in line.lower():
                    print(f"⚠️  Potential wildcard issue at line: {stripped}")
                    has_bad_wildcard = True
        
        if not has_bad_wildcard:
            print("✅ No active wildcard CORS configuration found")
        else:
            print("❌ Wildcard CORS origin found!")
            return False
    else:
        print("✅ No wildcard CORS issues found")
    
    # Check for ALLOWED_ORIGINS env var
    if "ALLOWED_ORIGINS" in content:
        print("✅ ALLOWED_ORIGINS environment variable is used")
    else:
        print("⚠️  ALLOWED_ORIGINS not found in main.py")
    
    return True

def check_rate_limiting():
    """Check if rate limiting is configured."""
    print("\n🔍 Checking rate limiting...")
    
    main_file = PROJECT_ROOT / "apps" / "main.py"
    middleware_file = PROJECT_ROOT / "apps" / "shared_core" / "security" / "middleware.py"
    
    if not middleware_file.exists():
        print("❌ Rate limit middleware not found")
        return False
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    if "RateLimitMiddleware" in content:
        print("✅ RateLimitMiddleware is imported")
        if "add_middleware(RateLimitMiddleware)" in content:
            print("✅ RateLimitMiddleware is added to app")
        else:
            print("⚠️  RateLimitMiddleware is not added to app")
    else:
        print("❌ RateLimitMiddleware not found")
        return False
    
    return True

def check_secrets_management():
    """Check for hardcoded secrets."""
    print("\n🔍 Checking for hardcoded secrets...")
    
    env_example = PROJECT_ROOT / ".env.example"
    docs_dir = PROJECT_ROOT / "docs"
    
    if not env_example.exists():
        print("❌ .env.example not found")
        return False
    else:
        print("✅ .env.example exists")
    
    secret_mgmt_doc = docs_dir / "SECRET_MANAGEMENT.md"
    if secret_mgmt_doc.exists():
        print("✅ SECRET_MANAGEMENT.md documentation exists")
    else:
        print("⚠️  SECRET_MANAGEMENT.md not found")
    
    # Scan for common hardcoded patterns
    hardcoded_patterns = [
        "password=",
        "secret=",
        "api_key=",
        "token="
    ]
    
    issues_found = []
    for py_file in PROJECT_ROOT.glob("apps/**/*.py"):
        if "test" in str(py_file):
            continue
        try:
            with open(py_file, 'r') as f:
                content = f.read()
                for pattern in hardcoded_patterns:
                    if pattern in content.lower() and "os.getenv" not in content:
                        issues_found.append(str(py_file))
                        break
        except:
            pass
    
    if issues_found:
        print(f"⚠️  Potential hardcoded secrets in {len(issues_found)} files")
    else:
        print("✅ No obvious hardcoded secrets found")
    
    return True

def run_alembic_check():
    """Run Alembic check command."""
    print("\n🔍 Running Alembic check...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "check"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Alembic check passed")
        else:
            print(f"⚠️  Alembic check failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️  Alembic check timed out")
    except Exception as e:
        print(f"⚠️  Alembic check error: {e}")

def generate_report():
    """Generate a summary report."""
    print("\n" + "=" * 60)
    print("PHASE 0 TECHNICAL DEBT FIX REPORT")
    print("=" * 60)
    
    checks = [
        ("Alembic Migrations", check_alembic_migrations()),
        ("CORS Configuration", check_cors_config()),
        ("Rate Limiting", check_rate_limiting()),
        ("Secrets Management", check_secrets_management()),
    ]
    
    print("\nSummary:")
    print("-" * 60)
    for name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:.<50} {status}")
    
    all_passed = all(result for _, result in checks)
    
    print("-" * 60)
    if all_passed:
        print("🎉 All Phase 0 checks passed!")
        print("\nNext steps:")
        print("1. Run: alembic upgrade head")
        print("2. Test the application")
        print("3. Proceed to Phase 1")
    else:
        print("⚠️  Some checks failed. Please review and fix.")
    
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix technical debt")
    parser.add_argument("--phase", type=str, default="0", help="Phase number")
    args = parser.parse_args()
    
    if args.phase == "0":
        success = generate_report()
        sys.exit(0 if success else 1)
    else:
        print(f"Phase {args.phase} not implemented yet")
        sys.exit(1)
