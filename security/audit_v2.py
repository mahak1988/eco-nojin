
#!/usr/bin/env python3
"""Spider Web Security Audit v2 — OWASP 2025 + DevSecOps 2026."""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def check_owasp_2025() -> list[str]:
    issues = []
    # A03: Supply Chain
    if not (ROOT / "security" / "sbom.json").exists():
        issues.append("A03: SBOM وجود ندارد (python security/supply_chain.py)")
    # A10: Exception Handling
    if not (ROOT / "security" / "middleware" / "exception_handler.py").exists():
        issues.append("A10: Exception Handler وجود ندارد")
    # A06: Dependency Audit
    r = subprocess.run([sys.executable, "-m", "pip", "show", "pip-audit"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        issues.append("A06: pip-audit نصب نیست")
    return issues

def check_nginx_cves() -> list[str]:
    issues = []
    r = subprocess.run(["nginx", "-v"], capture_output=True, text=True)
    if r.returncode == 0:
        version = r.stderr + r.stdout
        if "1.30" not in version and "1.31" not in version:
            issues.append("CVE-2026-42945/42530: Nginx باید به 1.31.0+ آپدیت شود")
    return issues

def check_zero_trust() -> list[str]:
    issues = []
    if not (ROOT / "security" / "zero_trust.py").exists():
        issues.append("Zero Trust config وجود ندارد")
    return issues

def main() -> int:
    print("=" * 60)
    print("  Spider Web Security Audit v2 — OWASP 2025")
    print("=" * 60)
    all_issues = []
    for name, fn in [
        ("OWASP 2025", check_owasp_2025),
        ("Nginx CVE-2026", check_nginx_cves),
        ("Zero Trust", check_zero_trust),
    ]:
        print(f"\n  [{name}]")
        issues = fn()
        all_issues.extend(issues)
        for i in issues:
            print(f"    ⚠️  {i}")
        if not issues:
            print("    ✅ OK")
    crit = len(all_issues)
    print(f"\n  Summary: {crit} issue(s)")
    return 1 if crit else 0

if __name__ == "__main__":
    sys.exit(main())
