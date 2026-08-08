#!/usr/bin/env python3
"""
Run ruff or black to format Python code consistently.
This script assumes ruff or black are installed in the environment.
"""

import subprocess
from pathlib import Path


def run_formatting_tool(tool_cmd: str, desc: str):
    """Helper to run a formatting tool command."""
    print(f"\n--- Running {desc} ---")
    print(f"Command: {tool_cmd}")
    try:
        result = subprocess.run(
            tool_cmd, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        if result.returncode != 0:
            print(f"Command '{tool_cmd}' failed with return code {result.returncode}")
        return result.returncode
    except FileNotFoundError:
        print(
            f"Command '{tool_cmd}' not found. Is it installed? Try 'pip install ruff' or 'pip install black'."
        )
        return 1


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    print(f"Formatting Python code in {project_root}/apps and {project_root}/scripts")

    # Prefer Ruff for speed and linting + formatting
    ruff_format_cmd = "ruff format apps/ scripts/"
    ruff_check_cmd = "ruff check apps/ scripts/ --fix"  # Also attempt to fix linting issues

    run_formatting_tool(ruff_check_cmd, "Ruff Linting and Auto-Fix")
    run_formatting_tool(ruff_format_cmd, "Ruff Formatting")

    print("\nCode formatting completed.")
