"""Compare apps/ between git HEAD and local working directory (normalizing line endings)."""
import os
import subprocess


def normalize(content: str) -> str:
    """Normalize CRLF to LF for comparison."""
    return content.replace("\r\n", "\n")


# Get repo file list
repo = subprocess.run(
    ["git", "ls-tree", "-r", "--name-only", "HEAD", "apps/"],
    capture_output=True,
    text=True,
).stdout.splitlines()

# Get local file list with normalized forward slashes
local = []
for dp, dirs, files in os.walk("apps"):
    dirs[:] = [d for d in dirs if d not in ("node_modules", "__pycache__", ".git")]
    for f in files:
        if f.endswith(".pyc") or f == "econojin.db":
            continue
        full = os.path.join(dp, f).replace("\\", "/")
        local.append(full)

repo_set = set(repo)
local_set = set(local)

only_repo = sorted(repo_set - local_set)
only_local = sorted(local_set - repo_set)

print("=== ONLY IN REPO (missing from local) ===")
for p in only_repo:
    print(p)
print(f"TOTAL: {len(only_repo)}")
print()

print("=== ONLY IN LOCAL (not tracked in repo) ===")
for p in only_local:
    print(p)
print(f"TOTAL: {len(only_local)}")
print()

# Check for files that differ in content (after normalizing line endings)
print("=== FILES WITH REAL CONTENT DIFFERENCES (after CRLF normalization) ===")
diff_count = 0
for p in sorted(repo_set & local_set):
    if os.path.isfile(p):
        repo_content = subprocess.run(
            ["git", "show", f"HEAD:{p}"],
            capture_output=True,
            text=True,
        ).stdout
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                local_content = f.read()
        except Exception:
            continue
        if normalize(repo_content) != normalize(local_content):
            diff_count += 1
            if diff_count <= 100:
                print(p)
print(f"TOTAL REAL DIFFERENCES: {diff_count}")