#!/usr/bin/env python3
"""
Moves redundant and junk files identified by triage_report.md to a quarantine directory.
This is a safer alternative to deletion.
"""

import shutil
from pathlib import Path


def quarantine_files(file_list, quarantine_dir):
    """Moves a list of files/dirs to the quarantine directory."""
    quarantine_path = Path(quarantine_dir)
    quarantine_path.mkdir(exist_ok=True)

    for item_path_str in file_list:
        item_path = Path(item_path_str)
        if item_path.exists():
            target_path = quarantine_path / item_path.name
            # Handle potential name conflicts in quarantine dir
            counter = 1
            original_target = target_path
            while target_path.exists():
                target_path = original_target.with_name(f"{original_target.stem}_{counter}{original_target.suffix}")
                counter += 1
            
            print(f"Moving {item_path} -> {target_path}")
            shutil.move(str(item_path), str(target_path))
        else:
            print(f"Warning: Item {item_path} not found, skipping.")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    quarantine_dir = project_root / "_QUARANTINE_MANUAL_REVIEW"

    # Example list based on triage_report.md
    # In a real scenario, this would be a comprehensive list from an automated scan.
    junk_items = [
        # ".env", # We won't move sensitive files automatically
        "log.txt",
        "quality_report.txt",
        # "scripts/api/.gaia_setup_backup", # Example nested path
        # "api/modules/ecocoin/router.py.backup", # Example backup file
    ]

    # Add more items from triage report or other sources
    # Let's simulate moving a dummy temp file for demonstration
    temp_file = project_root / "temp_to_delete.tmp"
    temp_file.touch() # Create a dummy file
    junk_items.append(temp_file)

    print(f"Starting quarantine process for {len(junk_items)} items into {quarantine_dir}/")
    quarantine_files(junk_items, quarantine_dir)
    print("Quarantine process complete. Please review the contents of the quarantine directory.")