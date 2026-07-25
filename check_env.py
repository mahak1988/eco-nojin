#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_env.py — بررسی متغیرهای محیطی مورد نیاز پروژه
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
بر اساس ساختار پروژه (AI, CMS, Contracts, Frontend) متغیرهای
مفقود را شناسایی و .env.example کامل می‌سازد.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ── متغیرهای مورد نیاز بر اساس بخش‌های پروژه ──
REQUIRED_VARS = {
    "Database": [
        ("DATABASE_URL", True, "postgresql://user:***@host:5432/db"),
        ("POSTGRES_PASSWORD", True, None),
    ],
    "Auth & Security": [
        ("SECRET_KEY", True, None),
        ("JWT_SECRET_KEY", True, None),
        ("FIRST_SUPERUSER_PASSWORD", True, None),
    ],
    "AI / LLM": [
        ("LLM_API_KEY", False, "sk-... (OpenAI/Anthropic/...)"),
        ("QDRANT_API_KEY", False, "کلید Qdrant Cloud"),
        ("QDRANT_URL", False, "https://xxx.qdrant.io:6333"),
        ("FAO_API_KEY", False, "کلید FAOSTAT API"),
    ],
    "CMS (Strapi)": [
        ("APP_KEYS", False, "key1,key2,key3,key4"),
        ("API_TOKEN_SALT", False, None),
        ("ADMIN_JWT_SECRET", False, None),
        ("TRANSFER_TOKEN_SALT", False, None),
    ],
    "Smart Contracts": [
        ("CONTRACT_DEPLOYER_KEY", False, "0x... (کلید خصوصی deployer)"),
        ("RPC_URL", False, "https://rpc.sepolia.org"),
        ("CONTRACT_ADDRESS", False, "0x... (آدرس EcoCoin)"),
    ],
    "Frontend": [
        ("VITE_API_URL", False, "http://localhost:8000"),
        ("VITE_CONTRACT_ADDRESS", False, "0x..."),
    ],
    "Infrastructure": [
        ("REDIS_URL", False, "redis://localhost:6379/0"),
        ("FRONTEND_HOST", False, "http://localhost:5173"),
    ],
}


def read_env(path: Path) -> dict[str, str]:
    """خواندن .env بدون نمایش مقادیر."""
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
    example_file = ROOT / ".env.example"

    print("═" * 60)
    print("  🔍 بررسی متغیرهای محیطی پروژه")
    print("═" * 60)
    if not apply:
        print("  ℹ️  حالت گزارش — برای ساخت .env.example: --apply")

    current_env = read_env(env_file)
    print(f"\n  📄 .env فعلی: {len(current_env)} متغیر")

    # ── بررسی هر بخش ──
    missing_critical = []
    missing_optional = []
    present = []

    for section, vars_list in REQUIRED_VARS.items():
        print(f"\n  ── {section} ──")
        for var_name, is_critical, hint in vars_list:
            if var_name in current_env:
                val = current_env[var_name]
                masked = f"{val[:4]}…{val[-3:]}" if len(val) > 10 else "****"
                print(f"     ✅ {var_name} = {masked}")
                present.append(var_name)
            else:
                status = "🔴" if is_critical else "🟡"
                hint_text = f"  ({hint})" if hint else ""
                print(f"     {status} {var_name} — مفقود{hint_text}")
                if is_critical:
                    missing_critical.append(var_name)
                else:
                    missing_optional.append((var_name, hint))

    # ── خلاصه ──
    print(f"\n{'═' * 60}")
    print(f"  📊 خلاصه:")
    print(f"     موجود: {len(present)}")
    print(f"     مفقود بحرانی: {len(missing_critical)}")
    print(f"     مفقود اختیاری: {len(missing_optional)}")

    if missing_critical:
        print(f"\n  🔴 متغیرهای بحرانی مفقود:")
        for v in missing_critical:
            print(f"     • {v}")

    # ── ساخت .env.example ──
    if apply:
        print(f"\n{'─' * 60}")
        print("  📝 ساخت .env.example …")
        lines = [
            "# ═══════════════════════════════════════════════════",
            "# econojin.com — Environment Variables Template",
            "# کپی کنید: cp .env.example .env",
            "# سپس مقادیر واقعی را وارد کنید",
            "# ⚠️ هرگز .env را commit نکنید",
            "# ═══════════════════════════════════════════════════",
            "",
        ]
        for section, vars_list in REQUIRED_VARS.items():
            lines.append(f"# ── {section} ──")
            for var_name, is_critical, hint in vars_list:
                if var_name in current_env:
                    lines.append(f"{var_name}=***")
                else:
                    placeholder = hint if hint else ""
                    req = " (REQUIRED)" if is_critical else ""
                    lines.append(f"{var_name}={placeholder}{req}")
            lines.append("")

        example_file.write_text("\n".join(lines), encoding="utf-8")
        print(f"  ✅ {example_file.name} ساخته شد ({len(lines)} خط)")

        # ── اطمینان از gitignore ──
        gi = ROOT / ".gitignore"
        gi_text = gi.read_text(encoding="utf-8") if gi.exists() else ""
        if ".env" not in gi_text:
            with gi.open("a", encoding="utf-8") as f:
                f.write("\n# Environment (هرگز commit نشود)\n.env\n.env.local\n.env.production\n")
            print("  ✅ .gitignore به‌روزرسانی شد")
        if ".env.example" in gi_text:
            print("  ⚠️  .env.example در gitignore است — باید commit شود!")
            print("     !.env.example را به gitignore اضافه کنید")

    print(f"\n{'═' * 60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())