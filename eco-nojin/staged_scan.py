#!/usr/bin/env python3
"""staged_scan.py â€” hook ظ‡ظˆط´ظ…ظ†ط¯: ظپظ‚ط· ظپط§غŒظ„â€Œظ‡ط§غŒ ظˆط§ظ‚ط¹غŒطŒ ظپظ‚ط· ط¨ط­ط±ط§ظ†غŒ ظ…ط³ط¯ظˆط¯ ط´ظˆط¯."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

try:
    from project_analyzer import ProjectAnalyzer, setup_logging
except ImportError:
    print("project_analyzer.py غŒط§ظپطھ ظ†ط´ط¯")
    sys.exit(2)

ROOT = Path(__file__).resolve().parent

# ظپظ‚ط· ظ…ظˆط§ط±ط¯ ط¨ط­ط±ط§ظ†غŒ commit ط±ط§ ظ…ط³ط¯ظˆط¯ ع©ظ†ظ†ط¯
FAIL_SEVERITIES = {"critical"}

# ظپط§غŒظ„â€Œظ‡ط§غŒ ط§ط¨ط²ط§ط± ط§ظ…ظ†غŒطھغŒ ظˆ ط®ط±ظˆط¬غŒâ€Œظ‡ط§ â€” ظ‡ط±ع¯ط² ط§ط³ع©ظ† ظ†ط´ظˆظ†ط¯ (ط®ظˆط¯-ط§ط±ط¬ط§ط¹غŒ)
SKIP_EXACT = {
    "project_analyzer.py", "secure_fix.py", "finalize_security.py",
    "cleanup_final.py", "fix_hook.py", "fix_hook_final.py", "staged_scan.py",
    "fix_git.py", "fix_config.py", "set_github_secrets.py", "find_and_fix_config.py", "auto_remediate.py", "project-analysis.json", "project-analysis.html",
    "project-analysis.sha256",
}
# ط§ظ„ع¯ظˆظ‡ط§غŒ ظ…ط³غŒط± â€” طھط³طھâ€Œظ‡ط§طŒ ع¯ط²ط§ط±ط´â€Œظ‡ط§طŒ storeظ‡ط§
SKIP_PATTERNS = (
    "/tests/", "/test_", "conftest.py", ".security_backup/", "reports/",
    ".pnpm-store/", "node_modules/", "__repo_sync_tmp__/", ".sync_backup_",
    "/i18n/locales/",
)


def get_staged_files() -> list[str]:
    r = subprocess.run(
        ["git", "-C", str(ROOT), "diff", "--cached",
         "--name-only", "--diff-filter=ACMR", "-z"],
        capture_output=True, text=True, check=False, timeout=30,
    )
    if r.returncode != 0:
        return []
    return [f for f in r.stdout.split("\0") if f.strip()]


def should_skip(rel: str) -> bool:
    normalized = rel.replace("\\", "/")
    name = normalized.split("/")[-1]
    if name in SKIP_EXACT:
        return True
    return any(p in normalized for p in SKIP_PATTERNS)


def main() -> int:
    staged = [f for f in get_staged_files() if not should_skip(f)]
    if not staged:
        print("ظ‡غŒع† ظپط§غŒظ„ ظ‚ط§ط¨ظ„ ط§ط³ع©ظ†غŒ staged ظ†غŒط³طھ")
        return 0

    print(f"ط§ط³ع©ظ† {len(staged)} ظپط§غŒظ„ staged â€¦")
    args = argparse.Namespace(
        max_file_mb=2.0, max_depth=12, exclude=[], no_network=True,
        no_git=True, fail_on="critical", json_out=".git/staged-scan.json",
        html_out=".git/staged-scan.html", verbose=False,
    )
    logger = setup_logging(False)
    analyzer = ProjectAnalyzer(ROOT, args, logger)
    analyzer._validate_root()
    for rel in staged:
        path = ROOT / rel
        if path.is_file():
            analyzer._process_file(path, rel)

    if analyzer.findings:
        print(f"  {len(analyzer.findings)} غŒط§ظپطھظ‡:")
        for f in analyzer.findings:
            loc = f"{f.file}:{f.line}" if f.line else f.file
            print(f"   [{f.severity}] {f.title} - {loc}")

    blocking = {f.severity for f in analyzer.findings} & FAIL_SEVERITIES
    if blocking:
        print(f"  commit ظ…ط³ط¯ظˆط¯ ط´ط¯ ({', '.join(sorted(blocking))})")
        print("     ط¹ط¨ظˆط± ظ…ظˆظ‚طھ: git commit --no-verify")
        return 1

    print(f"  {len(staged)} ظپط§غŒظ„ ظ¾ط§ع© ط¨ظˆط¯")
    return 0


if __name__ == "__main__":
    sys.exit(main())

