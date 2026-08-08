#!/usr/bin/env python3
"""
Run pytest with coverage for the apps directory.
This script assumes pytest and pytest-cov are installed in the environment.
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
    print(f"Measuring test coverage for {project_root}/apps")

    # Run pytest with coverage
    pytest_cov_cmd = "pytest --cov=apps --cov-report=html --cov-report=term-missing"
    run_command(pytest_cov_cmd, "Pytest Coverage Report")

    print(f"\nCheck the generated HTML report in {project_root}/htmlcov/ for detailed coverage information.")