#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
set_github_secrets_v3.py — تنظیم GitHub Secrets از Clipboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
توکن را از clipboard می‌خواند (بدون فایل، بدون input مستقیم، بدون masking).
"""
from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def get_clipboard() -> str:
    """خواندن محتوای clipboard (ویندوز/مک/لینوکس)."""
    try:
        if sys.platform == "win32":
            r = subprocess.run(["powershell", "-NoProfile", "-command",
                                "Get-Clipboard"],
                               capture_output=True, text=True, timeout=10)
            return r.stdout.strip()
        elif sys.platform == "darwin":
            r = subprocess.run(["pbpaste"], capture_output=True,
                               text=True, timeout=10)
            return r.stdout.strip()
        else:
            r = subprocess.run(["xclip", "-selection", "clipboard", "-o"],
                               capture_output=True, text=True, timeout=10)
            return r.stdout.strip()
    except Exception:
        return ""


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True, check=check, timeout=60)


def gh_api(url: str, auth_value: str, data: dict | None = None,
           method: str = "GET") -> tuple[dict, int]:
    headers = {
        "Authorization": "Bearer " + auth_value,
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
            return (json.loads(raw) if raw else {}), resp.status
    except urllib.error.HTTPError as exc:
        return {"error": exc.read().decode()[:200]}, exc.code
    except (urllib.error.URLError, OSError) as exc:
        return {"error": str(exc)}, 0


def main() -> int:
    print("═" * 60)
    print("  🔐 تنظیم GitHub Secrets (نسخه ۳ — Clipboard)")
    print("═" * 60)

    # ۱. خواندن توکن از clipboard
    print("\n  ⚠️  ابتدا توکن GitHub را کپی کنید (Ctrl+C)")
    print("     (github.com/settings/tokens → Generate new token → scope: repo)")
    input("     سپس اینجا Enter بزنید …")

    auth_value = get_clipboard()
    if not auth_value or len(auth_value) < 20:
        print("  ❌ clipboard خالی یا نامعتبر است")
        print("     → توکن را کپی کنید و دوباره اجرا کنید")
        return 1
    print(f"  ✅ توکن خوانده شد ({len(auth_value)} کاراکتر)")

    # ۲. اعتبارسنجی
    print("\n  → بررسی اعتبار …")
    data, status = gh_api("https://api.github.com/user", auth_value)
    if status != 200:
        msg = data.get("error", data.get("message", ""))[:120]
        print(f"  ❌ خطای {status}: {msg}")
        return 1
    print(f"  ✅ احراز هویت موفق: {data.get('login')}")

    # ۳. استخراج owner/repo
    r = git("remote", "get-url", "origin", check=False)
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", r.stdout.strip())
    if not m:
        print("  ❌ remote origin یافت نشد")
        return 1
    owner, repo = m.group(1), m.group(2)
    api_base = f"https://api.github.com/repos/{owner}/{repo}"
    print(f"  📦 مخزن: {owner}/{repo}")

    # ۴. خواندن رمزهای rotateشده
    creds_file = ROOT / ".security_backup" / "rotated_credentials.txt"
    if not creds_file.exists():
        print("  ❌ rotated_credentials.txt یافت نشد")
        return 1
    secrets_dict = {}
    for line in creds_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            secrets_dict[k.strip()] = v.strip()

    # ۵. PyNaCl
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
            print("  ❌ نصب PyNaCl ناموفق")
            return 1

    # ۶. دریافت public key
    pk_data, status = gh_api(f"{api_base}/actions/secrets/public-key", auth_value)
    if status != 200 or "key" not in pk_data:
        print(f"  ❌ دریافت public key ناموفق ({status})")
        return 1
    public_key_b64 = pk_data["key"]
    key_id = pk_data["key_id"]

    # ۷. رمزنگاری و ارسال secrets
    secret_names = ["DATABASE_URL", "QDRANT_API_KEY", "JWT_SECRET_KEY",
                    "FIRST_SUPERUSER_PASSWORD", "POSTGRES_PASSWORD", "SECRET_KEY"]
    ok_count = 0
    for name in secret_names:
        value = secrets_dict.get(name)
        if not value:
            continue
        pk = nacl.public.PublicKey(public_key_b64.encode(),
                                   nacl.encoding.Base64Encoder())
        encrypted = base64.b64encode(
            nacl.public.SealedBox(pk).encrypt(value.encode())).decode()
        result, status = gh_api(
            f"{api_base}/actions/secrets/{name}", auth_value,
            data={"encrypted_value": encrypted, "key_id": key_id},
            method="PUT")
        if status in (200, 201, 204):
            print(f"  ✅ {name}")
            ok_count += 1
        else:
            print(f"  ❌ {name} (خطای {status})")

    print(f"\n  🎉 {ok_count}/{len(secret_names)} secret تنظیم شد")
    if ok_count > 0:
        print("  ✅ GitHub Actions اکنون به رمزهای جدید دسترسی دارد")
    return 0


if __name__ == "__main__":
    sys.exit(main())