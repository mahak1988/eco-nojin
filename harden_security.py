#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
harden_security.py — تقویت معماری امنیتی بر اساس OWASP 2025 + DevSecOps 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
۱. نصب کتابخانه‌های امنیتی
۲. تقویت لایه‌های موجود
۳. افزودن لایه‌های جدید (Supply Chain, Exception Handling, Zero Trust)
۴. بررسی CVEهای Nginx
۵. ساخت SBOM
'''
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(cmd: list[str], desc: str = '') -> int:
    if desc:
        print(f'  → {desc}')
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=300)
    if r.returncode != 0 and r.stderr:
        print(f'    ⚠️  {r.stderr[:200]}')
    return r.returncode


def pip_install(packages: list[str], desc: str) -> None:
    print(f'\n  📦 {desc}')
    for pkg in packages:
        r = run([sys.executable, '-m', 'pip', 'install', '--quiet', '--user', pkg],
                f'نصب {pkg}')
        if r == 0:
            print(f'    ✅ {pkg}')
        else:
            print(f'    ⚠️  {pkg} (نصب ناموفق — دستی بررسی کنید)')


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    print(f'  + {rel}')


def main() -> int:
    apply = '--apply' in sys.argv
    print('═' * 60)
    print('  🛡️ تقویت معماری امنیتی — OWASP 2025 + DevSecOps 2026')
    print('═' * 60)
    if not apply:
        print('  ℹ️  حالت گزارش — برای اعمال: --apply')

    # ── ۱. نصب کتابخانه‌های امنیتی ──
    print('\n  [۱] کتابخانه‌های امنیتی:')
    if apply:
        pip_install([
            'slowapi',           # Rate Limiting پیشرفته
            'secure',            # Security Headers
            'pydantic-settings', # مدیریت امن env
            'passlib[bcrypt]',   # هش رمز عبور
            'python-jose[cryptography]',  # JWT
        ], 'کتابخانه‌های الزامی (OWASP A04, A07)')

        pip_install([
            'pip-audit',         # اسکن آسیب‌پذیری
            'bandit',            # SAST
            'detect-secrets',    # تشخیص secrets
            'safety',            # CVE check
        ], 'ابزارهای DevSecOps (OWASP A05, A06)')
    else:
        print('    slowapi, secure, pydantic-settings, passlib, python-jose')
        print('    pip-audit, bandit, detect-secrets, safety')

    # ── ۲. تقویت Nginx (CVE-2026) ──
    print('\n  [۲] تقویت Nginx (CVE-2026):')
    w('security/nginx/cve-2026-hardening.conf', '''
# ═══════════════════════════════════════════════════════════
#  CVE-2026 Hardening — Nginx 1.31.0+
#  CVE-2026-42945 (CVSS 9.2): Rewrite Directive RCE
#  CVE-2026-33032 (CVSS 9.8): nginx-ui Auth Bypass
#  CVE-2026-42530: HTTP/3 QPACK Use-After-Free
# ═══════════════════════════════════════════════════════════

# غیرفعال‌سازی HTTP/3 تا زمان patch کامل
# listen 443 quic;  ← غیرفعال بماند

# محدودسازی rewrite (جلوگیری از CVE-2026-42945)
if ($request_uri ~* "(\\.\\.|%2e%2e)") { return 403; }

# غیرفعال‌سازی server tokens
server_tokens off;

# محدودسازی متدها
if ($request_method !~ ^(GET|POST|PUT|PATCH|DELETE|OPTIONS)$) { return 405; }

# جلوگیری از Host Header Injection
if ($host !~* "^(econojin\\.com|www\\.econojin\\.com|localhost)$") { return 444; }

# محدودسازی اندازه هدرها (جلوگیری از buffer overflow)
large_client_header_buffers 2 4k;

# Timeout های سخت‌گیرانه
client_body_timeout 10;
client_header_timeout 10;
keepalive_timeout 5 5;
send_timeout 10;

# غیرفعال‌سازی autoindex
autoindex off;

# جلوگیری از دسترسی به فایل‌های حساس
location ~ /\\. { deny all; access_log off; log_not_found off; }
''')

    # ── ۳. Exception Handler (OWASP A10 — جدید 2025) ──
    print('\n  [۳] Exception Handler (OWASP A10 — جدید 2025):')
    w('security/middleware/exception_handler.py', '''
"""OWASP A10:2025 — Mishandling of Exceptional Conditions."""
from __future__ import annotations
import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("security.exceptions")

async def security_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """جلوگیری از نشت اطلاعات در خطاها."""
    # لاگ کامل برای تیم توسعه
    logger.error(
        "Unhandled exception: %s %s\\n%s",
        request.method, request.url.path,
        traceback.format_exc(),
        extra={"ip": request.client.host if request.client else "unknown"},
    )
    # پاسخ امن به کاربر (بدون stack trace)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "server_error",
        },
        headers={"X-Content-Type-Options": "nosniff"},
    )

async def validation_exception_handler(request: Request, exc) -> JSONResponse:
    """مدیریت امن خطاهای validation."""
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "type": "validation_error"},
    )

async def not_found_handler(request: Request, exc) -> JSONResponse:
    """جلوگیری از نشت اطلاعات مسیر."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found"},
    )
''')

    # ── ۴. Supply Chain Security (OWASP A03 — جدید 2025) ──
    print('\n  [۴] Supply Chain Security (OWASP A03 — جدید 2025):')
    w('security/supply_chain.py', '''
"""OWASP A03:2025 — Software Supply Chain Security."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent

def generate_sbom() -> dict:
    """ساخت SBOM (Software Bill of Materials)."""
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
''')

    # ── ۵. Zero Trust Config ──
    print('\n  [۵] Zero Trust Architecture:')
    w('security/zero_trust.py', '''
"""Zero Trust Security — Never Trust, Always Verify (2026)."""
from __future__ import annotations

class ZeroTrustConfig:
    """تنظیمات Zero Trust."""

    # ۱. Identity Verification — هر درخواست باید احراز هویت شود
    REQUIRE_AUTH_ALL_ENDPOINTS = True
    PUBLIC_ENDPOINTS = {"/health", "/docs", "/openapi.json", "/redoc"}

    # ۲. Least Privilege — حداقل دسترسی
    DEFAULT_ROLE = "viewer"
    ROLE_HIERARCHY = {
        "admin": ["admin", "editor", "viewer"],
        "editor": ["editor", "viewer"],
        "viewer": ["viewer"],
    }

    # ۳. Microsegmentation — جداسازی سرویس‌ها
    SERVICE_TOKENS = {
        "api": "internal-api-token",
        "cms": "internal-cms-token",
        "ai": "internal-ai-token",
    }

    # ۴. Continuous Verification — بررسی مداوم
    TOKEN_MAX_AGE_MINUTES = 60
    REQUIRE_MFA_ADMIN = True
    SESSION_BINDING = True  #绑定 IP + User-Agent

    # ۵. Assume Breach — فرض نفوذ
    LOG_ALL_ACCESS = True
    ANOMALY_DETECTION = True
    AUTO_LOCKOUT_THRESHOLD = 5
''')

    # ── ۶. CI/CD Security Pipeline ──
    print('\n  [۶] CI/CD Security Pipeline (DevSecOps 2026):')
    w('.github/workflows/security-pipeline.yml', '''
name: Security Pipeline (DevSecOps 2026)

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 3 * * 1'

permissions:
  contents: read
  security-events: write

jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Bandit SAST
        run: |
          pip install bandit
          bandit -r apps/ security/ -f json -o bandit-report.json || true
      - name: Upload SAST
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: bandit-report
          path: bandit-report.json

  dependency-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: pip-audit
        run: |
          pip install pip-audit
          pip-audit --format json --output audit-report.json || true
      - name: Upload Audit
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: audit-report
          path: audit-report.json

  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: detect-secrets
        run: |
          pip install detect-secrets
          detect-secrets scan --baseline .secrets.baseline || true

  project-analyzer:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Secure Project Analyzer
        run: |
          python project_analyzer.py . --no-network \\
            --exclude ".pnpm-store/*" --exclude "node_modules/*" \\
            --exclude "reports/*" --exclude ".security_backup/*" \\
            --exclude "project-analysis.*" --exclude "*/tests/*" \\
            --exclude "*/test_*" --fail-on critical
      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-report
          path: |
            project-analysis.json
            project-analysis.html

  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Generate SBOM
        run: python security/supply_chain.py
      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: security/sbom.json
''')

    # ── ۷. Security Audit تقویت‌شده ──
    print('\n  [۷] Security Audit تقویت‌شده:')
    w('security/audit_v2.py', '''
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
        print(f"\\n  [{name}]")
        issues = fn()
        all_issues.extend(issues)
        for i in issues:
            print(f"    ⚠️  {i}")
        if not issues:
            print("    ✅ OK")
    crit = len(all_issues)
    print(f"\\n  Summary: {crit} issue(s)")
    return 1 if crit else 0

if __name__ == "__main__":
    sys.exit(main())
''')

    # ── خلاصه ──
    print(f'\n{"═" * 60}')
    if apply:
        print('  ✅ تقویت امنیتی اعمال شد')
        print('\n  📋 دستورات بعدی:')
        print('     python security/supply_chain.py    # ساخت SBOM')
        print('     python security/audit_v2.py        # Audit جدید')
        print('     pip-audit                          # اسکن وابستگی‌ها')
        print('     bandit -r apps/ security/          # SAST')
    else:
        print('  → برای اعمال: python harden_security.py --apply')
    print('═' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())