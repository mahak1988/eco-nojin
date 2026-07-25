#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
set_github_secrets.py — تنظیم امن GitHub Secrets (نسخه ۲)
بدون getpass (جلوگیری از masking)، بدون gh CLI (REST API + PyNaCl)
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


def secure_input(prompt: str) -> str:
    """خواندن ورودی بدون نمایش در ترمینال (ویندوز/یونیکس)."""
    try:
        if sys.platform == "win32":
            import msvcrt
            print(prompt, end="", flush=True)
            chars: list[str] = []
            while True:
                ch = msvcrt.getwch()
                if ch in ("\r", "\n"):
                    break
                if ch in ("\b", "\x08"):
                    if chars:
                        chars.pop()
                        print("\b \b", end="", flush=True)
                    continue
                if ch == "\x03":
                    raise KeyboardInterrupt
                chars.append(ch)
                print("*", end="", flush=True)
            print()
            return "".join(chars)
        else:
            import termios
            import tty
            print(prompt, end="", flush=True)
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            chars = []
            try:
                tty.setraw(fd)
                while True:
                    ch = sys.stdin.read(1)
                    if ch in ("\r", "\n", "\x03"):
                        break
                    chars.append(ch)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
            print()
            return "".join(chars)
    except KeyboardInterrupt:
        print("\n  لغو شد")
        sys.exit(130)
    except Exception:
        return input(prompt)


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True, check=check, timeout=60)


def gh_api(url: str, token: str, data: dict | None = None,
           method: str = "GET") -> tuple[dict, int]:
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
            return (json.loads(raw) if raw else {}), resp.status
    except urllib.error.HTTPError as exc:
        return {"error": exc.read().decode()[:200]}, exc.code
    except (urllib.error.URLError, OSError) as exc:
        return {"error": str(exc)}, 0


def main() -> int:
    print("═" * 60)
    print("  🔐 تنظیم امن GitHub Secrets (نسخه ۲)")
    print("═" * 60)

    # ۱. دریافت توکن (امن، بدون نمایش)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token or len(token) < 20 or token == "***":
        print("\n  ساخت Personal Access Token:")
        print("  github.com/settings/tokens → Generate new token (classic)")
        print("  scope: ☑ repo | سپس کپی کنید (با ghp_ شروع می‌شود)\n")
        token = ***"  🔑 توکن را paste کنید (مخفی می‌ماند): ").strip()
        if not token or len(token) < 20:
            print("  ❌ توکن نامعتبر")
            return 1

    # ۲. اعتبارسنجی
    print("\n  → بررسی اعتبار توکن …")
    data, status = gh_api("https://api.github.com/user", token)
    if status != 200:
        print(f"  ❌ خطای {status}: {data.get('error', data.get('message', ''))[:120]}")
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
    pk_data, status = gh_api(f"{api_base}/actions/secrets/public-key", token)
    if status != 200 or "key" not in pk_data:
        print(f"  ❌ دریافت public key ناموفق ({status})")
        print("  → scope=repo و فعال‌بودن Actions را بررسی کنید")
        return 1
    public_key_b64 = pk_data["key"]
    key_id = pk_data["key_id"]

    # ۷. رمزنگاری و ارسال secrets
    secret_names = ["DATABASE_URL", "QDRANT_API_KEY", "JWT_SECRET_KEY",
                    "FIRST_SUPERUSER_PASSWORD", "POSTGRES_PASSWORD"]
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
            f"{api_base}/actions/secrets/{name}", token,
            data={"encrypted_value": encrypted, "key_id": key_id},
            method="PUT")
        if status in (200, 201, 204):
            print(f"  ✅ {name}")
            ok_count += 1
        else:
            print(f"  ❌ {name} (خطای {status})")

    print(f"\n  🎉 {ok_count}/{len(secret_names)} secret تنظیم شد")
    return 0


if __name__ == "__main__":
    sys.exit(main())