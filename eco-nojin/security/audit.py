
#!/usr/bin/env python3
"""Spider Web Security - Automated Audit."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main() -> int:
    print("=" * 60)
    print("  Spider Web Security Audit")
    print("=" * 60)
    issues = []
    gi = ROOT / ".gitignore"
    if gi.exists():
        c = gi.read_text(encoding="utf-8")
        for p in [".env", "*.pem", "*.key"]:
            if p not in c:
                issues.append(f"WARN: {p} not in .gitignore")
    for f in ["security/middleware/security_middleware.py",
              "security/middleware/anti_phishing.py",
              "security/middleware/ai_security.py",
              "security/config.py",
              "security/nginx/security-headers.conf"]:
        if not (ROOT / f).exists():
            issues.append(f"MISSING: {f}")
    env = ROOT / ".env"
    if env.exists():
        c = env.read_text(encoding="utf-8")
        if re.search(r"(?i)(password|secret|key)\s*=\s*(changeme|password|123456|admin)", c):
            issues.append("CRITICAL: weak password in .env")
    crit = len([i for i in issues if i.startswith("CRITICAL")])
    warn = len([i for i in issues if i.startswith("WARN")])
    miss = len([i for i in issues if i.startswith("MISSING")])
    for i in issues:
        print(f"  {i}")
    if not issues:
        print("  All checks passed")
    print(f"\n  Summary: {crit} critical | {warn} warn | {miss} missing")
    return 1 if crit else 0

if __name__ == "__main__":
    sys.exit(main())
