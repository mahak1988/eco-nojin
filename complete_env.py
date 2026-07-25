#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
complete_env.py — تکمیل خودکار متغیرهای مفقود .env
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• متغیرهای محلی (salts, keys) → تولید خودکار
• متغیرهای frontend/infra → مقادیر پیش‌فرض
• متغیرهای خارجی → راهنمایی
"""
from __future__ import annotations

import re
import secrets
import string
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def gen_key(length: int = 32) -> str:
    return secrets.token_hex(length)


def gen_salt(length: int = 32) -> str:
    return secrets.token_urlsafe(length)[:length]


def gen_app_keys(count: int = 4) -> str:
    return ",".join(secrets.token_hex(16) for _ in range(count))


# ── متغیرهایی که خودکار تولید می‌شوند ──
AUTO_VARS = {
    "APP_KEYS": lambda: gen_app_keys(4),
    "API_TOKEN_SALT": lambda: gen_salt(32),
    "ADMIN_JWT_SECRET": lambda: gen_salt(32),
    "TRANSFER_TOKEN_SALT": lambda: gen_salt(32),
}

# ── متغیرهایی با مقدار پیش‌فرض ──
DEFAULT_VARS = {
    "VITE_API_URL": "http://localhost:8000",
    "FRONTEND_HOST": "http://localhost:5173",
    "REDIS_URL": "redis://localhost:6379/0",
    "RPC_URL": "https://rpc.sepolia.org",
}

# ── متغیرهایی که نیاز به اقدام خارجی دارند ──
EXTERNAL_VARS = {
    "LLM_API_KEY": (
        "OpenAI: platform.openai.com/api-keys\n"
        "     Anthropic: console.anthropic.com/settings/keys\n"
        "     مقدار: sk-... یا sk-ant-..."
    ),
    "FAO_API_KEY": (
        "FAOSTAT: fao.org → API Key Registration\n"
        "     مقدار: کلید API دریافتی"
    ),
    "CONTRACT_DEPLOYER_KEY": (
        "MetaMask → Account Details → Export Private Key\n"
        "     مقدار: 0x... (۶۴ کاراکتر hex)\n"
        "     ⚠️ فقط برای testnet استفاده شود!"
    ),
    "CONTRACT_ADDRESS": (
        "پس از deploy قرارداد EcoCoin\n"
        "     مقدار: 0x... (آدرس قرارداد)"
    ),
    "VITE_CONTRACT_ADDRESS": (
        "مشابه CONTRACT_ADDRESS\n"
        "     مقدار: 0x... (آدرس قرارداد)"
    ),
}


def read_env(path: Path) -> dict[str, str]:
    env = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


def main() -> int:
    apply = "--apply" in sys.argv
    env_file = ROOT / ".env"

    print("═" * 60)
    print("  🔧 تکمیل خودکار .env")
    print("═" * 60)
    if not apply:
        print("  ℹ️  حالت گزارش — برای اعمال: --apply")

    current = read_env(env_file)
    added = []
    skipped = []

    # ── ۱. متغیرهای خودکار ──
    print("\n  [۱] متغیرهای محلی (تولید خودکار):")
    for var, generator in AUTO_VARS.items():
        if var in current:
            print(f"     ✅ {var} — موجود")
            skipped.append(var)
        else:
            value = generator()
            masked = f"{value[:6]}…{value[-4:]}"
            print(f"     🔑 {var} = {masked}")
            if apply:
                current[var] = value
            added.append(var)

    # ── ۲. مقادیر پیش‌فرض ──
    print("\n  [۲] متغیرهای frontend/infra (پیش‌فرض):")
    for var, default in DEFAULT_VARS.items():
        if var in current:
            print(f"     ✅ {var} — موجود")
            skipped.append(var)
        else:
            print(f"     🌐 {var} = {default}")
            if apply:
                current[var] = default
            added.append(var)

    # ── ۳. متغیرهای خارجی ──
    print("\n  [۳] متغیرهای خارجی (نیاز به اقدام دستی):")
    for var, guide in EXTERNAL_VARS.items():
        if var in current:
            print(f"     ✅ {var} — موجود")
            skipped.append(var)
        else:
            print(f"     🟡 {var} — مفقود")
            for line in guide.split("\n"):
                print(f"        {line}")

    # ── ۴. نوشتن .env ──
    if apply and added:
        print(f"\n{'─' * 60}")
        print(f"  📝 به‌روزرسانی .env ({len(added)} متغیر جدید) …")

        # خواندن محتوای فعلی و افزودن متغیرهای جدید
        text = env_file.read_text(encoding="utf-8") if env_file.exists() else ""

        # گروه‌بندی برای خوانایی
        sections = {
            "CMS (Strapi)": ["APP_KEYS", "API_TOKEN_SALT",
                             "ADMIN_JWT_SECRET", "TRANSFER_TOKEN_SALT"],
            "Frontend": ["VITE_API_URL", "FRONTEND_HOST"],
            "Infrastructure": ["REDIS_URL"],
            "Smart Contracts": ["RPC_URL"],
        }

        additions = []
        for section, vars_list in sections.items():
            section_vars = [(v, current[v]) for v in vars_list
                            if v in current and v in added]
            if section_vars:
                additions.append(f"\n# ── {section} ──")
                for k, v in section_vars:
                    additions.append(f"{k}={v}")

        if additions:
            text += "\n" + "\n".join(additions) + "\n"
            env_file.write_text(text, encoding="utf-8")
            print(f"  ✅ .env به‌روزرسانی شد")

    # ── خلاصه ──
    print(f"\n{'═' * 60}")
    print(f"  📊 خلاصه:")
    print(f"     افزوده‌شده: {len(added)}")
    print(f"     موجود (قبلی): {len(skipped)}")
    print(f"     نیاز به اقدام خارجی: "
          f"{len([v for v in EXTERNAL_VARS if v not in current])}")

    if not apply:
        print(f"\n  → برای اعمال: python complete_env.py --apply")
    print("═" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())