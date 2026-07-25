#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_secret_key.py — تولید SECRET_KEY و افزودن به .env و GitHub Secrets
"""
from __future__ import annotations

import base64
import json
import re
import secrets as _sec
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def gen_key(length: int = 64) -> str:
    return _sec.token_urlsafe(length)[:length]


def gh_api(url: str, auth: str, data: dict | None = None,
           method: str = "GET") -> tuple[dict, int]:
    headers = {
        "Authorization": "Bearer " + auth,
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
    print("=" * 60)
    print("  SECRET_KEY — Generate & Deploy")
    print("=" * 60)

    # ۱. تولید SECRET_KEY
    secret_key = gen_key(64)
    print(f"  🔑 SECRET_KEY = {secret_key[:6]}…{secret_key[-4:]} ({len(secret_key)} chars)")

    # ۲. افزودن به .env
    env_file = ROOT / ".env"
    if env_file.exists():
        text = env_file.read_text(encoding="utf-8")
        if re.search(r'^SECRET_KEY=.*$', text, re.MULTILINE):
            text = re.sub(r'^SECRET_KEY=.*$', f'SECRET_KEY=***',
                          text, flags=re.MULTILINE)
        else:
            text += f'\nSECRET_KEY=***\n'
        env_file.write_text(text, encoding="utf-8")
        print("  ✅ .env به‌روزرسانی شد")

    # ۳. افزودن به rotated_credentials.txt
    creds = ROOT / ".security_backup" / "rotated_credentials.txt"
    if creds.exists():
        text = creds.read_text(encoding="utf-8")
        if "SECRET_KEY=" not in text:
            text += f'\nSECRET_KEY=***\n'
            creds.write_text(text, encoding="utf-8")
            print("  ✅ rotated_credentials.txt به‌روزرسانی شد")

    # ۴. GitHub Secrets
    token_file = ROOT / ".gh_token"
    if not token_file.exists():
        print("\n  📋 برای تنظیم GitHub Secret:")
        print("     notepad .gh_token  → توکن را paste → Ctrl+S")
        print("     python add_secret_key.py  (اجرای مجدد)")
        return 0

    auth = token_file.read_text(encoding="utf-8").strip()
    if not auth or len(auth) < 30 or not auth.isascii():
        print("  ❌ توکن در .gh_token نامعتبر است")
        return 1

    r = subprocess.run(["git", "-C", str(ROOT), "remote", "get-url", "origin"],
                       capture_output=True, text=True, check=False)
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", r.stdout.strip())
    if not m:
        print("  ❌ remote origin یافت نشد")
        return 1
    owner, repo = m.group(1), m.group(2)
    api_base = f"https://api.github.com/repos/{owner}/{repo}"

    pk_data, status = gh_api(f"{api_base}/actions/secrets/public-key", auth)
    if status != 200 or "key" not in pk_data:
        print(f"  ❌ دریافت public key ناموفق ({status})")
        return 1

    try:
        import nacl.encoding
        import nacl.public
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install",
                        "pynacl", "--quiet", "--user"], check=False)
        import nacl.encoding
        import nacl.public

    pk = nacl.public.PublicKey(pk_data["key"].encode(),
                               nacl.encoding.Base64Encoder())
    encrypted = base64.b64encode(
        nacl.public.SealedBox(pk).encrypt(secret_key.encode())).decode()
    result, status = gh_api(
        f"{api_base}/actions/secrets/SECRET_KEY", auth,
        data={"encrypted_value": encrypted, "key_id": pk_data["key_id"]},
        method="PUT")
    if status in (200, 201, 204):
        print("  ✅ GitHub Secret: SECRET_KEY تنظیم شد")
        print("\n  🎉 6/6 secrets کامل شد")
    else:
        print(f"  ❌ خطای {status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())