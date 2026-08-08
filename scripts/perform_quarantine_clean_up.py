#!/usr/bin/env python3
"""
Systematically moves junk files and backups identified in triage_report.md to a quarantine directory.
This script reads a predefined list of files/directories and moves them.
"""

import shutil
from pathlib import Path


def perform_quarantine_clean_up(file_list, backup_dir_name="_QUARANTINE_AUTOMATED"):
    """Moves a list of files/dirs to a quarantine directory."""
    project_root = Path(__file__).resolve().parent.parent
    quarantine_path = project_root / backup_dir_name
    quarantine_path.mkdir(exist_ok=True)

    print(
        f"Starting automated quarantine process for {len(file_list)} items into {quarantine_path}/"
    )
    for item_path_str in file_list:
        item_path = project_root / item_path_str  # Resolve relative to project root
        if item_path.exists():
            target_path = quarantine_path / item_path.name
            # Handle potential name conflicts in quarantine dir
            counter = 1
            original_target = target_path
            while target_path.exists():
                target_path = original_target.with_name(
                    f"{original_target.stem}_{counter}{original_target.suffix}"
                )
                counter += 1

            print(f"  Moving {item_path} -> {target_path}")
            shutil.move(str(item_path), str(target_path))
        else:
            print(f"  Warning: Item {item_path} not found, skipping.")

    print("Automated quarantine process complete.")


if __name__ == "__main__":
    # List of junk items identified from triage_report.md or similar sources
    # This is a static list for demonstration. A real system might read this from a config file or a more dynamic source.
    junk_items = [
        # Junk Scripts (example entries)
        "add_approval_system.py",
        "add_languages.py",
        # Redundant Backups
        ".contracts_backup",
        ".i18n_backup",
        ".venv.backup",
        "backups",
        # Local Backups
        "api/modules/ecocoin/router.py.backup",
        "apps/web/package.json.backup",
        # Temp Reports
        "log.txt",
        "quality_report.txt",
        "requirements-fix.txt",
        "requirements-missing-fixed.txt",
        "requirements-missing.txt",
        "requirements.txt",
        "requirements_new.txt",
        # Note: Sensitive files like .env are typically NOT moved automatically and are handled separately.
    ]

    # In a real scenario, you'd likely want to confirm this action before proceeding!
    print(
        "WARNING: This script will move files. Please review the 'junk_items' list in the script."
    )
    response = input("Do you want to proceed with the quarantine? (yes/no): ")
    if response.lower() in ["yes", "y"]:
        perform_quarantine_clean_up(junk_items)
    else:
        print("Quarantine process cancelled by user.")
