#!/usr/bin/env python3
"""
Run bandit and pip-audit security scans.
This script assumes bandit and pip-audit are installed in the environment.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, desc: str):
    """Helper to run a shell command and print output."""
    print(f"\n--- Running {desc} ---")
    print(f"Command: {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        if result.returncode != 0:
            print(f"Command '{cmd}' failed with return code {result.returncode}")
        return result.returncode
    except FileNotFoundError:
        print(f"Command '{cmd}' not found. Is it installed?")
        return 1


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    print(f"Running security scans on {project_root}")

    # Run bandit scan on the apps directory
    bandit_cmd = "bandit -r apps/ -ll -ii"
    run_command(bandit_cmd, "Bandit Security Scan")

    # Run pip-audit on requirements file
    req_file = project_root / "requirements.txt"
    if req_file.exists():
        pip_audit_cmd = f"pip-audit --requirement {req_file}"
        run_command(pip_audit_cmd, "Pip-Audit Dependency Scan")
    else:
        print(f"Requirements file {req_file} not found, skipping pip-audit.")