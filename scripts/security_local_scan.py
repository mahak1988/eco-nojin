#!/usr/bin/env python3
"""Phase 4 — free local security scan (bandit + optional pip-audit).

Usage:
  python scripts/security_local_scan.py
  python scripts/security_local_scan.py --audit
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> int:
    print("+", " ".join(cmd))
    r = subprocess.run(cmd, cwd=ROOT)
    return int(r.returncode)


def main() -> int:
    p = argparse.ArgumentParser(description="Econojin local security scan")
    p.add_argument("--audit", action="store_true", help="Also run pip-audit on requirements.txt")
    p.add_argument("--fail-high", action="store_true", help="Exit non-zero on high+ bandit findings")
    args = p.parse_args()

    if not shutil.which("bandit") and not _ensure_bandit():
        print("bandit not available; pip install bandit", file=sys.stderr)
        return 2

    bandit_cmd = [
        sys.executable,
        "-m",
        "bandit",
        "-r",
        "apps",
        "-c",
        "bandit.yaml",
        "-ll",
        "-f",
        "txt",
    ]
    code = run(bandit_cmd)
    # bandit returns 1 when findings exist
    if args.fail_high and code != 0:
        print("Bandit reported issues (--fail-high)")
        return code

    if args.audit:
        if shutil.which("pip-audit") or _ensure_pip_audit():
            run([sys.executable, "-m", "pip_audit", "-r", "requirements.txt"])
        else:
            print("pip-audit not installed; skip")

    print("\nOK — local security scan finished (free tools only).")
    return 0


def _ensure_bandit() -> bool:
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "bandit"],
            cwd=ROOT,
        )
        return True
    except Exception:
        return False


def _ensure_pip_audit() -> bool:
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "pip-audit"],
            cwd=ROOT,
        )
        return True
    except Exception:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
