#!/usr/bin/env python3
"""
Repository Sync Checker v2.0
Accurately parses git status --porcelain to categorize uncommitted changes.
"""

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

@dataclass
class GitFileChange:
    status_code: str
    file_path: str

    @property
    def human_readable_status(self) -> str:
        status_map = {
            'M': 'Modified (Working Tree)',
            'A': 'Added (Staged)',
            'D': 'Deleted',
            'R': 'Renamed',
            'C': 'Copied',
            'U': 'Unmerged (Conflict)',
            '?': 'Untracked',
            'M_': 'Modified (Staged)',
            'MM': 'Modified (Staged & Working Tree)',
        }
        return status_map.get(self.status_code, f'Status: {self.status_code}')

@dataclass
class SyncReport:
    repo_path: Path
    branch: str
    is_git_repo: bool = True
    fetch_successful: bool = False
    remote_available: bool = False
    
    uncommitted_changes: List[GitFileChange] = field(default_factory=list)
    unpushed_commits_count: int = 0
    unpulled_commits_count: int = 0
    errors: List[str] = field(default_factory=list)

class GitCommandError(Exception):
    pass

def run_git_command(cmd: List[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    full_cmd = ['git'] + cmd
    try:
        result = subprocess.run(
            full_cmd, cwd=cwd, capture_output=True, text=True, check=check, encoding='utf-8'
        )
        return result
    except subprocess.CalledProcessError as e:
        raise GitCommandError(e.stderr.strip() or f"Exit code {e.returncode}") from e
    except FileNotFoundError as e:
        raise GitCommandError("Git executable not found in PATH.") from e

def generate_report(repo_path_str: str) -> SyncReport:
    repo_path = Path(repo_path_str).resolve()
    report = SyncReport(repo_path=repo_path, branch="unknown")

    if not repo_path.exists():
        report.is_git_repo = False
        report.errors.append(f"Path does not exist: {repo_path}")
        return report

    try:
        if run_git_command(['rev-parse', '--is-inside-work-tree'], repo_path, check=False).returncode != 0:
            report.is_git_repo = False
            report.errors.append("Not a valid Git repository.")
            return report
    except GitCommandError as e:
        report.is_git_repo = False
        report.errors.append(str(e))
        return report

    try:
        report.branch = run_git_command(['branch', '--show-current'], repo_path).stdout.strip() or "HEAD (detached)"
    except GitCommandError:
        pass

    try:
        run_git_command(['fetch', '--all', '--quiet'], repo_path, check=False)
        report.fetch_successful = True
        report.remote_available = True
    except GitCommandError:
        report.errors.append("Failed to fetch from remote. Showing local status only.")

    # Robust Porcelain Parsing
    try:
        status_result = run_git_command(['status', '--porcelain'], repo_path)
        for line in status_result.stdout.splitlines():
            if not line.strip():
                continue
            
            # Format is "XY path" where X is index, Y is working tree, followed by a space
            raw_status = line[0:2]
            file_path = line[3:].strip()
            
            # Determine the most relevant status code for display
            if raw_status == '??':
                status_code = '?'
            elif raw_status[1] != ' ':
                # Working tree has changes (e.g., ' M', ' D', 'MM')
                status_code = raw_status if raw_status == 'MM' else raw_status[1]
            else:
                # Only index has changes (e.g., 'M ', 'A ')
                status_code = raw_status[0] + '_' if raw_status[0] == 'M' else raw_status[0]
                
            report.uncommitted_changes.append(GitFileChange(status_code, file_path))
            
    except GitCommandError as e:
        report.errors.append(f"Failed to get status: {e}")

    if report.remote_available and report.branch != "HEAD (detached)":
        try:
            rev_list_result = run_git_command(['rev-list', '--left-right', '--count', f'HEAD...@{{upstream}}'], repo_path, check=False)
            if rev_list_result.returncode == 0:
                counts = rev_list_result.stdout.strip().split()
                if len(counts) == 2:
                    report.unpushed_commits_count = int(counts[0])
                    report.unpulled_commits_count = int(counts[1])
        except GitCommandError:
            report.errors.append("No upstream branch configured.")

    return report

def print_report(report: SyncReport):
    print(f"\n{Color.BOLD}{'='*60}{Color.END}")
    print(f"{Color.BOLD}Git Sync & Working Directory Status Report{Color.END}")
    print(f"{'='*60}\n")

    if not report.is_git_repo:
        print(f"{Color.RED}❌ Error: Not a Git repository.{Color.END}")
        return

    print(f"{Color.BLUE}📂 Path:{Color.END}   {report.repo_path}")
    print(f"{Color.BLUE}🌿 Branch:{Color.END} {report.branch}")
    
    if report.errors:
        print(f"\n{Color.YELLOW}⚠️ Warnings:{Color.END}")
        for err in report.errors:
            print(f"  - {err}")

    # Group changes by type for cleaner output
    untracked = [c for c in report.uncommitted_changes if c.status_code == '?']
    modified = [c for c in report.uncommitted_changes if c.status_code in ['M', 'M_', 'MM']]
    deleted = [c for c in report.uncommitted_changes if c.status_code == 'D']
    added = [c for c in report.uncommitted_changes if c.status_code == 'A']
    others = [c for c in report.uncommitted_changes if c.status_code not in ['?', 'M', 'M_', 'MM', 'D', 'A']]

    print(f"\n{Color.BOLD}--- Working Directory Summary ---{Color.END}")
    print(f"Total Uncommitted Items: {Color.BOLD}{len(report.uncommitted_changes)}{Color.END}")
    
    if untracked:
        print(f"{Color.MAGENTA}❓ Untracked Files:{Color.END} {len(untracked)}")
        for c in untracked[:10]: # Show max 10 to prevent console spam
            print(f"  {Color.MAGENTA}?{Color.END} {c.file_path}")
        if len(untracked) > 10:
            print(f"  {Color.MAGENTA}... and {len(untracked) - 10} more untracked files.{Color.END}")

    if modified:
        print(f"{Color.YELLOW}✏️  Modified Files:{Color.END} {len(modified)}")
        for c in modified[:10]:
            print(f"  {Color.YELLOW}M{Color.END} {c.file_path}")
        if len(modified) > 10:
            print(f"  {Color.YELLOW}... and {len(modified) - 10} more modified files.{Color.END}")

    if deleted:
        print(f"{Color.RED}❌ Deleted Files:{Color.END} {len(deleted)}")
        for c in deleted:
            print(f"  {Color.RED}D{Color.END} {c.file_path}")

    if added:
        print(f"{Color.GREEN}➕ Added (Staged) Files:{Color.END} {len(added)}")
        for c in added[:5]:
            print(f"  {Color.GREEN}A{Color.END} {c.file_path}")

    if others:
        print(f"{Color.CYAN}🔹 Other Changes (Renamed, Unmerged, etc.):{Color.END} {len(others)}")

    print(f"\n{Color.BOLD}--- Commit Synchronization ---{Color.END}")
    if report.unpushed_commits_count > 0 or report.unpulled_commits_count > 0:
        print(f"{Color.CYAN}⬆️  Unpushed Commits:{Color.END} {report.unpushed_commits_count}")
        print(f"{Color.CYAN}⬇️  Unpulled Commits:{Color.END} {report.unpulled_commits_count}")
    else:
        if report.remote_available:
            print(f"{Color.GREEN}✔ Branch is up to date with remote.{Color.END}")
        else:
            print(f"{Color.YELLOW}⚠️ Cannot verify sync status.{Color.END}")

    print(f"\n{Color.BOLD}{'='*60}{Color.END}\n")

def main():
    target_path = sys.argv[1] if len(sys.argv) > 1 else "."
    try:
        report = generate_report(target_path)
        print_report(report)
        if report.uncommitted_changes or report.unpushed_commits_count > 0:
            sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"{Color.RED}Critical error: {e}{Color.END}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()