#!/usr/bin/env python3
"""
set_secrets_final.py — تنظیم GitHub Secrets (روش file-based، با اعتبارسنجی)
"""
from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True, check=check, timeout=60)


def gh_api(url: str, auth_value: str, data: dict | None = None,
           method: str = "GET") -> tuple[dict, int]:
    if not auth_value.isascii():
        return {"error": "non-ASCII in token"}, 0
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
    print("=" * 60)
    print("  GitHub Secrets — Final (file-based)")
    print("=" * 60)

    # ۱. خواندن توکن از فایل
    token_file = ROOT / ".gh_token"
    if not token_file.exists():
        print("  ❌ .gh_token یافت نشد")
        print("     notepad .gh_token  → توکن را paste → Ctrl+S → ببندید")
        return 1

    auth_value = token_file.read_text(encoding="utf-8").strip()

    # ۲. اعتبارسنجی توکن
    if not auth_value or len(auth_value) < 30:
        print(f"  ❌ توکن خیلی کوتاه است ({len(auth_value)} کاراکتر). باید ۴۰+ باشد")
        return 1
    if not auth_value.isascii():
        print("  ❌ توکن حاوی کاراکتر غیر-ASCII است!")
        print("     مطمئن شوید فقط توکن (ghp_...) در فایل باشد، نه متن فارسی")
        return 1
    if not auth_value.startswith(("ghp_", "github_pat_", "gho_", "ghs_", "ghr_")):
        print(f"  ⚠️  توکن با ghp_/github_pat_ شروع نمی‌شود ({auth_value[:4]}...)")

    print(f"  📋 توکن: {len(auth_value)} کاراکتر، شروع: {auth_value[:4]}…")

    # ۳. اعتبارسنجی با GitHub
    print("  → بررسی اعتبار …")
    data, status = gh_api("https://api.github.com/user", auth_value)
    if status != 200:
        msg = data.get("error", data.get("message", ""))[:120]
        print(f"  ❌ خطای {status}: {msg}")
        return 1
    print(f"  ✅ احراز هویت موفق: {data.get('login')}")

    # ۴. استخراج owner/repo
    r = git("remote", "get-url", "origin", check=False)
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", r.stdout.strip())
    if not m:
        print("  ❌ remote origin یافت نشد")
        return 1
    owner, repo = m.group(1), m.group(2)
    api_base = f"https://api.github.com/repos/{owner}/{repo}"
    print(f"  📦 مخزن: {owner}/{repo}")

    # ۵. خواندن رمزهای rotateشده
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

    # ۶. PyNaCl
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

    # ۷. دریافت public key
    pk_data, status = gh_api(f"{api_base}/actions/secrets/public-key", auth_value)
    if status != 200 or "key" not in pk_data:
        print(f"  ❌ دریافت public key ناموفق ({status})")
        print("     → scope=repo و فعال‌بودن Actions را بررسی کنید")
        return 1

    # ۸. رمزنگاری و ارسال secrets
    secret_names = ["DATABASE_URL", "QDRANT_API_KEY", "JWT_SECRET_KEY",
                    "FIRST_SUPERUSER_PASSWORD", "POSTGRES_PASSWORD", "SECRET_KEY"]
    ok_count = 0
    for name in secret_names:
        value = secrets_dict.get(name)
        if not value:
            continue
        pk = nacl.public.PublicKey(pk_data["key"].encode(),
                                   nacl.encoding.Base64Encoder())
        encrypted = base64.b64encode(
            nacl.public.SealedBox(pk).encrypt(value.encode())).decode()
        result, status = gh_api(
            f"{api_base}/actions/secrets/{name}", auth_value,
            data={"encrypted_value": encrypted, "key_id": pk_data["key_id"]},
            method="PUT")
        if status in (200, 201, 204):
            print(f"  ✅ {name}")
            ok_count += 1
        else:
            print(f"  ❌ {name} (خطای {status})")

    print(f"\n  🎉 {ok_count}/{len(secret_names)} secret تنظیم شد")
    if ok_count > 0:
        print("  ✅ GitHub Actions به رمزهای جدید دسترسی دارد")
    return 0


if __name__ == "__main__":
    sys.exit(main())
