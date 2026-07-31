
"""OWASP A03:2025 — Software Supply Chain Security."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def generate_sbom() -> dict:
    """ساخت SBOM (Software Bill of Materials)."""
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "metadata": {
            "timestamp": datetime.now(UTC).isoformat(),
            "component": {"name": "econojin.com", "type": "application"},
        },
        "components": [],
    }
    # pip packages
    r = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        capture_output=True, text=True, timeout=60,
    )
    if r.returncode == 0:
        for pkg in json.loads(r.stdout):
            sbom["components"].append({
                "type": "library",
                "name": pkg["name"],
                "version": pkg["version"],
                "purl": f"pkg:pypi/{pkg['name']}@{pkg['version']}",
            })
    return sbom

def audit_dependencies() -> int:
    """بررسی آسیب‌پذیری وابستگی‌ها."""
    print("  → pip-audit …")
    r = subprocess.run(
        [sys.executable, "-m", "pip_audit", "--format", "json"],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode == 0:
        print("  ✅ بدون آسیب‌پذیری شناخته‌شده")
    else:
        try:
            vulns = json.loads(r.stdout)
            print(f"  ⚠️  {len(vulns)} آسیب‌پذیری یافت شد")
            for v in vulns[:5]:
                print(f"    • {v.get('name','?')} {v.get('version','?')}: {v.get('id','?')}")
        except Exception:
            print("  ⚠️  خطا در تحلیل نتایج")
    return r.returncode

if __name__ == "__main__":
    sbom = generate_sbom()
    out = ROOT / "security" / "sbom.json"
    out.write_text(json.dumps(sbom, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  ✅ SBOM: {out} ({len(sbom['components'])} component)")
    audit_dependencies()
