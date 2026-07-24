#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_hook.py — جایگزینی hook کند با hook سریع staged_scan.py"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CONFIG = """\
repos:
  - repo: local
    hooks:
      - id: staged-secret-scan
        name: Staged Secret Scan (fast, <1s)
        entry: python staged_scan.py
        language: system
        pass_filenames: false
        always_run: true
        stages: [pre-commit]
"""


def main() -> None:
    (ROOT / ".pre-commit-config.yaml").write_text(CONFIG, encoding="utf-8")
    print("✅ .pre-commit-config.yaml → staged_scan.py (اسکن <۱ ثانیه)")
    r = subprocess.run([sys.executable, "-m", "pre_commit", "install"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode == 0:
        print("✅ hook مجدداً نصب شد")
    else:
        print(f"⚠️  نصب hook: {r.stderr.strip()}")


if __name__ == "__main__":
    main()