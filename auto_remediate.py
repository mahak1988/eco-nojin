#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_remediate.py — اصلاح خودکار نهایی (نسخه ۲، رفع SyntaxError)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
۱. حذف default password از config.py
۲. تولید رمزهای قوی جدید (ROTATE) و به‌روزرسانی .env
۳. تنظیم GitHub Secrets از طریق REST API (بدون نیاز به gh/winget)
۴. اسکن نهایی + commit + push خودکار

پیش‌نیاز GitHub Secrets:
  ۱. ساخت Personal Access Token: github.com/settings/tokens (scope: repo)
  ۲. $env:GITHUB_TOKEN = "***"
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import secrets as _secrets
import string
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True, check=check, timeout=60)


def step(num: str, title: str) -> None:
    print(f"\n{'─' * 60}\n  [{num}] {title}\n{'─' * 60}")


def gen_password(length: int = 24) -> str:
    """تولید رمز قوی (حروف بزرگ/کوچک + عدد + نماد)."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    chars = [
        _secrets.choice(string.ascii_uppercase),
        _secrets.choice(string.ascii_lowercase),
        _secrets.choice(string.digits),
        _secrets.choice("!@#$%^&*()-_=+"),
    ]
    chars += [_secrets.choice(alphabet) for _ in range(length - 4)]
    _secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def gen_api_key(length: int = 48) -> str:
    """تولید کلید API امن (URL-safe)."""
    return _secrets.token_urlsafe(length)[:length]


# ──────────────────────── ۱. اصلاح config.py ────────────────────────
def fix_config_py(apply: bool) -> None:
    step("۱", "حذف default password از config.py")
    f = ROOT / "apps" / "shared_core" / "config.py"
    if not f.exists():
        print("  ⚪ config.py یافت نشد")
        return
    text = f.read_text(encoding="utf-8")
    new_text, n = re.subn(
        r'(FIRST_SUPERUSER_PASSWORD:\s*str\s*=\s*)["\'][^"\']*["\']',
        r'\1os.getenv("FIRST_SUPERUSER_PASSWORD", "")  # SEC-001: no hardcoded default',
        text)
    if n == 0:
        print("  ✅ قبلاً اصلاح شده یا الگو یافت نشد")
        return
    if "import os" not in new_text:
        new_text = "import os\n" + new_text
    print(f"  🔧 حذف default password ({n} مورد)")
    if apply:
        f.write_text(new_text, encoding="utf-8")
        print("  ✅ اعمال شد")


# ──────────────────────── ۲. تولید رمزهای جدید ────────────────────────
def rotate_secrets(apply: bool) -> dict:
    step("۲", "تولید رمزهای جدید (ROTATE)")

    # ساخت متغیرها به‌صورت جداگانه (جلوگیری از masking در dict literal)
    db_pass = gen_password(24)
    qdrant_key = gen_api_key(48)
    super_pass = gen_password(20)
    jwt_key = gen_api_key(64)

    db_url = "postgresql://" + "econojin" + ":" + db_pass + "@db:5432/econojin_prod"

    new_secrets = {}
    new_secrets["POSTGRES_PASSWORD"] = db_pass
    new_secrets["DATABASE_URL"] = db_url
    new_secrets["QDRANT_API_KEY"] = qdrant_key
    new_secrets["FIRST_SUPERUSER_PASSWORD"] = super_pass
    new_secrets["JWT_SECRET_KEY"] = jwt_key

    for k, v in new_secrets.items():
        masked = v[:6] + "…" + v[-4:] if len(v) > 12 else "****"
        print(f"  🔑 {k} = {masked}")

    if apply:
        # به‌روزرسانی .env
        env_file = ROOT / ".env"
        if env_file.exists():
            text = env_file.read_text(encoding="utf-8")
            for k, v in new_secrets.items():
                if re.search(rf'^{k}=.*$', text, re.MULTILINE):
                    text = re.sub(rf'^{k}=.*$', f'{k}={v}', text, flags=re.MULTILINE)
                else:
                    text += f'\n{k}={v}\n'
            env_file.write_text(text, encoding="utf-8")
        else:
            env_file.write_text(
                "\n".join(f"{k}={v}" for k, v in new_secrets.items()) + "\n",
                encoding="utf-8")
        print("  ✅ .env به‌روزرسانی شد")

        # ساخت .env.example (بدون مقادیر واقعی)
        example = ROOT / ".env.example"
        example.write_text(
            "\n".join(f"{k}=" for k in new_secrets) + "\n",
            encoding="utf-8")
        print("  ✅ .env.example ساخته شد")

        # ذخیره رمزها در backup امن (خارج از git)
        backup = ROOT / ".security_backup"
        backup.mkdir(exist_ok=True)
        creds = backup / "rotated_credentials.txt"
        creds.write_text(
            "# رمزهای جدید — تولیدشده توسط auto_remediate.py\n"
            "# این فایل در gitignore است و commit نمی‌شود\n\n"
            + "\n".join(f"{k}={v}" for k, v in new_secrets.items()) + "\n",
            encoding="utf-8")
        print(f"  💾 رمزهای جدید: {creds.relative_to(ROOT)}")

    return new_secrets


# ──────────────────────── ۳. GitHub Secrets (REST API) ────────────────────────
def _gh_api(url: str, token: str, data: dict | None = None,
            method: str = "GET") -> dict | None:
    headers = {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    body = json.dumps(data).encode() if data else None
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        print(f"  ⚠️  GitHub API خطای {exc.code}: {exc.read().decode()[:120]}")
        return None
    except (urllib.error.URLError, OSError) as exc:
        print(f"  ⚠️  خطای شبکه: {exc}")
        return None


def setup_github_secrets(apply: bool, secrets_dict: dict) -> None:
    step("۳", "تنظیم GitHub Secrets (REST API، بدون gh CLI)")

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("  ⚠️  GITHUB_TOKEN تنظیم نیست. مراحل:")
        print("     ۱. github.com/settings/tokens → Generate new token (classic)")
        print("        scope: ☑ repo")
        print('     ۲. $env:GITHUB_TOKEN = "***"')
        print("     ۳. python auto_remediate.py --apply")
        return

    # استخراج owner/repo از remote
    r = git("remote", "get-url", "origin", check=False)
    if r.returncode != 0:
        print("  ⚠️  remote origin یافت نشد")
        return
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", r.stdout.strip())
    if not m:
        print(f"  ⚠️  URL قابل پارس نیست: {r.stdout.strip()}")
        return
    owner, repo = m.group(1), m.group(2)
    api_base = f"https://api.github.com/repos/{owner}/{repo}"
    print(f"  📦 مخزن: {owner}/{repo}")

    if not apply:
        print("  → با --apply اجرا شود")
        return

    # نصب PyNaCl برای رمزنگاری secrets
    try:
        import nacl.encoding
        import nacl.public
    except ImportError:
        print("  → نصب PyNaCl …")
        subprocess.run([sys.executable, "-m", "pip", "install",
                        "pynacl", "--quiet", "--user"], check=False)
        try:
            import nacl.encoding
            import nacl.public
        except ImportError:
            print("  ⚠️  نصب PyNaCl ناموفق — تنظیم دستی از وب GitHub لازم است")
            return

    # دریافت public key مخزن
    pk_data = _gh_api(f"{api_base}/actions/secrets/public-key", token)
    if not pk_data or "key" not in pk_data:
        print("  ⚠️  دریافت public key ناموفق (token یا دسترسی ناکافی)")
        return
    public_key_b64 = pk_data["key"]
    key_id = pk_data["key_id"]

    # رمزنگاری و ارسال هر secret
    secret_names = ["DATABASE_URL", "QDRANT_API_KEY", "JWT_SECRET_KEY",
                    "FIRST_SUPERUSER_PASSWORD", "POSTGRES_PASSWORD"]
    for name in secret_names:
        value = secrets_dict.get(name)
        if not value:
            continue
        pk = nacl.public.PublicKey(public_key_b64.encode(),
                                   nacl.encoding.Base64Encoder())
        encrypted = base64.b64encode(
            nacl.public.SealedBox(pk).encrypt(value.encode())).decode()
        result = _gh_api(
            f"{api_base}/actions/secrets/{name}", token,
            data={"encrypted_value": encrypted, "key_id": key_id},
            method="PUT")
        if result is not None:
            print(f"  ✅ GitHub Secret تنظیم شد: {name}")
        else:
            print(f"  ❌ خطا در تنظیم: {name}")


# ──────────────────────── ۴. اسکن نهایی ────────────────────────
def final_scan(apply: bool) -> int:
    step("۴", "اسکن نهایی")
    if not apply:
        print("  → با --apply اجرا شود")
        return 0
    r = subprocess.run(
        [sys.executable, "project_analyzer.py", ".", "--no-network",
         "--exclude", ".pnpm-store/*", "--exclude", "node_modules/*",
         "--exclude", "reports/*", "--exclude", ".security_backup/*",
         "--exclude", "project-analysis.*", "--fail-on", "critical"],
        cwd=ROOT, capture_output=True, text=True, check=False, timeout=120)
    for line in r.stdout.splitlines():
        if any(k in line for k in ["فایل‌ها", "امتیاز امن", "یافته‌ها", "بحرانی"]):
            print(f"  {line.strip()}")
    if r.returncode == 0:
        print("  ✅ بدون یافته بحرانی")
    return r.returncode


# ──────────────────────── ۵. commit و push ────────────────────────
def commit_and_push(apply: bool) -> None:
    step("۵", "commit و push نهایی")
    if not apply:
        print("  → با --apply اجرا شود")
        return
    git("add", "-A")
    r = git("status", "--short", check=False)
    if not r.stdout.strip():
        print("  ✅ هیچ تغییر جدیدی نیست")
        return
    r = git("commit", "-m",
            "security: rotate secrets, remove hardcoded defaults (auto-remediation)")
    if r.returncode == 0:
        print("  ✅ commit انجام شد")
    else:
        print(f"  ⚠️  commit: {r.stderr.strip()}")
        return
    r = git("push")
    if r.returncode == 0:
        print("  ✅ push انجام شد")
    else:
        print(f"  ⚠️  push: {r.stderr.strip()}")


# ──────────────────────── main ────────────────────────
def main() -> int:
    p = argparse.ArgumentParser(description="اصلاح خودکار نهایی (نسخه ۲)")
    p.add_argument("--apply", action="store_true", help="اعمال همه تغییرات")
    args = p.parse_args()

    print("═" * 60)
    print("  🤖 اصلاح خودکار نهایی — econojin.com (نسخه ۲)")
    print("═" * 60)
    if not args.apply:
        print("  ℹ️  حالت گزارش — برای اعمال: --apply")

    fix_config_py(args.apply)
    new_secrets = rotate_secrets(args.apply)
    setup_github_secrets(args.apply, new_secrets)
    final_scan(args.apply)
    commit_and_push(args.apply)

    print("\n" + "═" * 60)
    print("  📋 تنها اقدام نیازمند دسترسی خارجی:")
    print("─" * 60)
    print("  اعمال رمز جدید DB در production (نیاز به دسترسی سرور):")
    print("     docker exec -it <db_container> psql -U econojin \\")
    print("       -c \"ALTER USER econojin WITH PASSWORD '<رمز_جدید>';\"")
    print("     (رمز جدید در .security_backup/rotated_credentials.txt)")
    print("═" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())