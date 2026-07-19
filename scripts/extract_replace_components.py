#!/usr/bin/env python3
"""
Component Extraction & Replacement Script
Extracts and integrates components from GitHub frontend projects:
- salvia-kit/salvia-kit (Dashboards, UI components)
- alan2207/bulletproof-react (Architecture patterns, hooks)
- aminju14/agri-moon (GIS, agriculture components)
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any

# Configuration
BASE_DIR = Path(__file__).parent.parent
REPOS_DIR = BASE_DIR / "repos"
WEB_SRC = BASE_DIR / "apps" / "web" / "src"

GITHUB_REPOS = {
    "salvia-kit": "https://github.com/salvia-kit/salvia-kit.git",
    "bulletproof-react": "https://github.com/alan2207/bulletproof-react.git",
    "agri-moon": "https://github.com/aminju14/agri-moon.git",
}


def clone_repos() -> None:
    """Clone GitHub repositories with shallow depth."""
    REPOS_DIR.mkdir(exist_ok=True)
    
    for name, url in GITHUB_REPOS.items():
        repo_path = REPOS_DIR / name
        if not repo_path.exists():
            print(f"Cloning {name}...")
            subprocess.run(
                ["git", "clone", "--depth", "1", url, str(repo_path)],
                check=True,
                capture_output=True
            )
        else:
            print(f"Repository {name} already exists, skipping.")


def extract_component_data() -> dict[str, Any]:
    """Extract component metadata from cloned repositories."""
    result = {}
    
    for name in GITHUB_REPOS.keys():
        repo_path = REPOS_DIR / name
        if repo_path.exists():
            # Find component directories
            components = list(repo_path.rglob("*"))
            result[name] = [str(p.relative_to(repo_path)) for p in components if p.suffix in [".tsx", ".ts", ".jsx", ".js"]]
    
    return result


def generate_report(components: dict[str, Any]) -> None:
    """Generate integration report."""
    report_path = REPOS_DIR / "integration_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(components, f, indent=2, ensure_ascii=False)
    print(f"Report saved to {report_path}")


def main() -> None:
    """Main entry point."""
    print("Starting component extraction...")
    clone_repos()
    components = extract_component_data()
    generate_report(components)
    print("Extraction complete!")


if __name__ == "__main__":
    main()