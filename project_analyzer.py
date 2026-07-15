#!/usr/bin/env python3
"""
Project Analyzer | تحلیل‌گر پروژه نرم‌افزاری
==================================================
A generic, dependency-free Python script that inspects ANY software project
directory and produces a comprehensive analysis report covering:

  1. Project overview (root path, total size, file count)
  2. Directory tree (top 3 levels, with ignored dirs filtered out)
  3. Language / file-type distribution (with LOC counting)
  4. Detected tech stack (config files → ecosystem mapping)
  5. Dependencies (parsed from package.json, requirements.txt, go.mod, etc.)
  6. Entry points (main.py, index.js, main.go, Cargo.toml, ...)
  7. Test files
  8. Documentation files
  9. CI/CD configuration
 10. Docker / containerization
 11. Version control status (git branch, last commit, remote)
 12. Largest files (top 10)
 13. Potential issues (secrets, missing README, oversized files, ...)

Usage:
    python3 project_analyzer.py [PATH] [--json] [--depth N] [--no-loc]

If PATH is omitted, the current working directory is used.

The script is read-only: it never modifies, creates, or deletes anything.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────

# Map file extensions to human-readable language names.
LANGUAGE_MAP: dict[str, str] = {
    ".py": "Python",
    ".pyi": "Python (stub)",
    ".js": "JavaScript",
    ".jsx": "JavaScript (JSX)",
    ".mjs": "JavaScript (ESM)",
    ".cjs": "JavaScript (CJS)",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (TSX)",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".scala": "Scala",
    ".rb": "Ruby",
    ".php": "PHP",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".swift": "Swift",
    ".m": "Objective-C",
    ".mm": "Objective-C++",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".ps1": "PowerShell",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
    ".less": "LESS",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".sql": "SQL",
    ".r": "R",
    ".R": "R",
    ".pl": "Perl",
    ".pm": "Perl",
    ".lua": "Lua",
    ".dart": "Dart",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".erl": "Erlang",
    ".clj": "Clojure",
    ".cljs": "ClojureScript",
    ".hs": "Haskell",
    ".fs": "F#",
    ".fsx": "F#",
    ".nim": "Nim",
    ".zig": "Zig",
    ".v": "V",
    ".jl": "Julia",
    ".ml": "OCaml",
    ".tf": "Terraform",
    ".dockerfile": "Dockerfile",
    ".makefile": "Make",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".toml": "TOML",
    ".json": "JSON",
    ".xml": "XML",
    ".md": "Markdown",
    ".rst": "reStructuredText",
    ".txt": "Plain Text",
    ".csv": "CSV",
    ".tsv": "TSV",
    ".env": "Env",
    ".ini": "INI",
    ".cfg": "Config",
    ".conf": "Config",
}

# Map config file names to the ecosystem / tool they indicate.
CONFIG_FILES: dict[str, str] = {
    "package.json": "Node.js / JavaScript package",
    "package-lock.json": "npm lockfile",
    "yarn.lock": "Yarn lockfile",
    "pnpm-lock.yaml": "pnpm lockfile",
    "tsconfig.json": "TypeScript configuration",
    "jsconfig.json": "JavaScript configuration",
    "pyproject.toml": "Python (modern, PEP 518)",
    "requirements.txt": "Python (pip requirements)",
    "requirements-dev.txt": "Python (dev requirements)",
    "Pipfile": "Python (Pipenv)",
    "Pipfile.lock": "Python (Pipenv lockfile)",
    "poetry.lock": "Python (Poetry lockfile)",
    "setup.py": "Python (legacy packaging)",
    "setup.cfg": "Python (setup config)",
    "go.mod": "Go module",
    "go.sum": "Go checksums",
    "Cargo.toml": "Rust (Cargo manifest)",
    "Cargo.lock": "Rust (Cargo lockfile)",
    "pom.xml": "Java (Maven)",
    "build.gradle": "Java/Kotlin (Gradle)",
    "build.gradle.kts": "Kotlin (Gradle)",
    "build.sbt": "Scala (sbt)",
    "mix.exs": "Elixir (Mix)",
    "rebar.config": "Erlang (rebar3)",
    "Gemfile": "Ruby (Bundler)",
    "Gemfile.lock": "Ruby (lockfile)",
    "composer.json": "PHP (Composer)",
    "composer.lock": "PHP (lockfile)",
    "Dockerfile": "Docker container",
    "docker-compose.yml": "Docker Compose",
    "docker-compose.yaml": "Docker Compose",
    "Jenkinsfile": "Jenkins CI",
    ".gitlab-ci.yml": "GitLab CI",
    ".travis.yml": "Travis CI",
    "Makefile": "Make build",
    "CMakeLists.txt": "CMake build",
    "babel.config.js": "Babel transpiler",
    "babel.config.json": "Babel transpiler",
    ".babelrc": "Babel (legacy)",
    "webpack.config.js": "Webpack bundler",
    "webpack.config.ts": "Webpack bundler",
    "vite.config.ts": "Vite bundler",
    "vite.config.js": "Vite bundler",
    "next.config.js": "Next.js framework",
    "next.config.mjs": "Next.js framework",
    "next.config.ts": "Next.js framework",
    "nuxt.config.ts": "Nuxt framework",
    "nuxt.config.js": "Nuxt framework",
    "angular.json": "Angular framework",
    "vue.config.js": "Vue CLI",
    "tailwind.config.js": "Tailwind CSS",
    "tailwind.config.ts": "Tailwind CSS",
    "postcss.config.js": "PostCSS",
    "eslint.config.js": "ESLint (flat config)",
    "eslint.config.mjs": "ESLint (flat config)",
    ".eslintrc.json": "ESLint",
    ".eslintrc.js": "ESLint",
    ".eslintrc.yml": "ESLint",
    "tslint.json": "TSLint (deprecated)",
    ".prettierrc": "Prettier",
    ".prettierrc.json": "Prettier",
    ".prettierrc.js": "Prettier",
    "prettier.config.js": "Prettier",
    "jest.config.js": "Jest tests",
    "jest.config.ts": "Jest tests",
    "vitest.config.ts": "Vitest",
    "vitest.config.js": "Vitest",
    "pytest.ini": "pytest",
    "tox.ini": "tox",
    ".flake8": "Flake8",
    "mypy.ini": "mypy",
    ".mypy.ini": "mypy",
    "ruff.toml": "Ruff linter",
    ".ruff.toml": "Ruff linter",
    "alembic.ini": "Alembic (DB migrations)",
    "prisma/schema.prisma": "Prisma ORM",
    "tailwind.config.cjs": "Tailwind CSS",
    ".editorconfig": "Editor config",
    ".pre-commit-config.yaml": "Pre-commit hooks",
    "LICENSE": "License file",
    "LICENSE.md": "License file",
    "LICENSE.txt": "License file",
    "README.md": "README documentation",
    "README.rst": "README documentation",
    "README.txt": "README documentation",
    "README": "README documentation",
    "CHANGELOG.md": "Changelog",
    "CONTRIBUTING.md": "Contributing guide",
    "CODE_OF_CONDUCT.md": "Code of conduct",
    ".gitignore": "Git ignore rules",
    ".gitattributes": "Git attributes",
    ".env": "Environment variables (SENSITIVE)",
    ".env.local": "Env local (SENSITIVE)",
    ".env.example": "Env template (safe to commit)",
    ".env.sample": "Env template (safe to commit)",
}

# Directories that are typically generated, vendored, or cache — skip them.
# These are matched EXACTLY (case-sensitive) against directory names, OR via glob.
IGNORE_DIRS: set[str] = {
    # ── VCS & metadata ──
    ".git", ".hg", ".svn", ".bzr",
    # ── Node.js / JavaScript ──
    "node_modules", ".pnpm-store", ".yarn", ".yarn-cache", ".turbo",
    ".next", ".nuxt", ".output", ".svelte-kit", ".astro", ".remix",
    ".parcel-cache", ".cache", ".fusebox", ".webpack",
    # ── Python ──
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".tox", ".eggs", "*.egg-info", ".ipynb_checkpoints", ".dmypy.json",
    # ── Python virtual envs (also match .venv-1, .venv-2, venv-3, etc.) ──
    ".venv", "venv", "env", ".env", "env.bak", "venv.bak",
    # ── Build / artifact dirs ──
    "dist", "build", "out", "target", "bin", "obj",
    "vendor", "_vendor", "_build", "deps",
    # ── IDE / editor ──
    ".idea", ".vscode", ".fleet", ".history",
    # ── Test coverage ──
    "coverage", ".nyc_output", ".nyc_output",
    # ── JVM ──
    ".gradle", ".mvn", ".gradle-build", ".kotlinc",
    # ── Terraform / IaC ──
    ".terraform", ".terragrunt-cache", "terraform.tfstate.d",
    # ── Other runtimes ──
    ".deno", ".bun", ".stack-work", "Pods", "DerivedData",
    # ── Misc temp ──
    "tmp", "temp", ".tmp",
}

# Common entry-point file names (top-level only).
ENTRY_POINT_NAMES: set[str] = {
    "main.py", "app.py", "run.py", "manage.py", "wsgi.py", "asgi.py",
    "server.py", "__main__.py", "cli.py",
    "index.js", "index.ts", "main.js", "main.ts", "app.js", "app.ts",
    "server.js", "server.ts", "start.js", "start.ts", "cli.js", "cli.ts",
    "main.go", "main.rs", "main.java", "Main.java", "App.java",
    "Program.cs", "main.rb", "config.ru",
    "index.html",  # static site entry
    "Cargo.toml",  # Rust manifest = entry signal
    "go.mod",
}

# Patterns for test files (matched against file name).
TEST_PATTERNS: list[str] = [
    r"^test_.*\.py$", r".*_test\.py$", r".*\.test\.(js|ts|jsx|tsx)$",
    r".*\.spec\.(js|ts|jsx|tsx)$", r".*_test\.go$", r"^.*_test\.go$",
    r".*Test\.java$", r".*\.test\.rs$", r".*_test\.rs$",
    r".*\.spec\.rb$", r".*_test\.rb$", r".*\.test\.cs$",
    r"__tests__", r"tests?\.ts$", r"tests?\.js$",
]

# File extensions considered documentation.
DOC_EXTENSIONS: set[str] = {".md", ".rst", ".txt", ".adoc", ".asciidoc", ".org"}

# Comment markers per language (for LOC heuristic).
COMMENT_MARKERS: dict[str, str] = {
    "Python": "#",
    "Shell": "#",
    "YAML": "#",
    "TOML": "#",
    "Ruby": "#",
    "Perl": "#",
    "R": "#",
    "JavaScript": "//",
    "TypeScript": "//",
    "Go": "//",
    "Rust": "//",
    "Java": "//",
    "Kotlin": "//",
    "Scala": "//",
    "C": "//",
    "C++": "//",
    "C#": "//",
    "Swift": "//",
    "SQL": "--",
    "Lua": "--",
    "Haskell": "--",
}


# ─────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────────────────────────────────

@dataclass
class FileInfo:
    rel_path: str
    abs_path: str
    ext: str
    size: int
    mtime: float
    language: str = ""


@dataclass
class ProjectReport:
    root: str
    analyzed_at: str
    focus: str = ""             # subdir under analysis ("" = whole project)
    total_files: int = 0
    total_size_bytes: int = 0
    total_loc: int = 0
    files_by_language: dict = field(default_factory=dict)
    loc_by_language: dict = field(default_factory=dict)
    largest_files: list = field(default_factory=list)
    detected_configs: dict = field(default_factory=dict)
    dependencies: dict = field(default_factory=dict)
    entry_points: list = field(default_factory=list)
    test_files: list = field(default_factory=list)
    doc_files: list = field(default_factory=list)
    ci_cd: list = field(default_factory=list)
    docker_files: list = field(default_factory=list)
    git_info: dict = field(default_factory=dict)
    directory_tree: str = ""
    issues: list = field(default_factory=list)
    errors: list = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────
# CORE ANALYZER
# ─────────────────────────────────────────────────────────────────────

class ProjectAnalyzer:
    """Walks a project directory and produces a ProjectReport.

    Parameters
    ----------
    root : Path
        The project root (where .git, package.json, etc. live).
    max_depth : int
        Maximum directory depth to walk.
    count_loc : bool
        Whether to count lines of code (slower).
    focus : str or None
        If set, restrict analysis to this subdirectory (e.g. "apps").
        The root is still used for git/config/manifest detection, but the
        file walk, language stats, and tree are scoped to the focus dir.
        Useful for monorepos where the "real" code lives in apps/ or packages/.
    """

    def __init__(self, root: Path, max_depth: int = 12, count_loc: bool = True,
                 focus: Optional[str] = None):
        self.root = root.resolve()
        self.max_depth = max_depth
        self.count_loc = count_loc
        self.focus = focus.strip().strip("/\\") if focus else ""
        # Effective walk root: focus subdir if specified, else root itself
        self.walk_root = (self.root / self.focus).resolve() if self.focus else self.root
        self.files: list[FileInfo] = []
        self.errors: list[str] = []

    # ---- 1. Walk the filesystem ------------------------------------
    def walk(self) -> None:
        if not self.walk_root.exists():
            raise FileNotFoundError(f"Path not found: {self.walk_root}")
        if not self.walk_root.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.walk_root}")

        for dirpath, dirnames, filenames in os.walk(self.walk_root):
            # Filter ignored directories in-place (modifies os.walk iteration)
            dirnames[:] = [d for d in dirnames if not self._is_ignored_dir(d)]

            # Enforce depth limit (relative to walk_root, not project root)
            try:
                rel = Path(dirpath).relative_to(self.walk_root)
                depth = len(rel.parts)
            except ValueError:
                depth = 0
            if depth > self.max_depth:
                dirnames[:] = []
                continue

            for fname in filenames:
                fpath = Path(dirpath) / fname
                try:
                    stat = fpath.stat()
                    ext = fpath.suffix.lower()
                    # Special-case files without extension but known names
                    if not ext and fname.lower() in {"dockerfile", "makefile",
                                                      "jenkinsfile", "rakefile",
                                                      "gemfile", "license", "readme"}:
                        ext = "." + fname.lower()
                    language = LANGUAGE_MAP.get(ext, "")
                    # rel_path is always relative to the PROJECT ROOT,
                    # so config/manifest detection from self.root still works.
                    try:
                        rel_to_root = str(fpath.relative_to(self.root))
                    except ValueError:
                        rel_to_root = str(fpath)  # outside root (shouldn't happen)
                    self.files.append(FileInfo(
                        rel_path=rel_to_root,
                        abs_path=str(fpath),
                        ext=ext,
                        size=stat.st_size,
                        mtime=stat.st_mtime,
                        language=language,
                    ))
                except (PermissionError, OSError) as e:
                    self.errors.append(f"{fpath}: {e}")

    def _is_ignored_dir(self, name: str) -> bool:
        # Exact match (case-sensitive)
        if name in IGNORE_DIRS:
            return True
        # Match versioned venv patterns: .venv-1, .venv-2, venv-3.8, venv-3.11, etc.
        if re.match(r'^(?:\.)?venv-\d+(?:\.\d+)*$', name, re.IGNORECASE):
            return True
        if re.match(r'^env-\d+(?:\.\d+)*$', name, re.IGNORECASE):
            return True
        # Match Python egg-info dirs: my_package.egg-info, my-package.egg-info
        if name.endswith(".egg-info") or name.endswith(".egg-link"):
            return True
        # Match __pycache__ variants: __pycache__.something
        if name.startswith("__pycache__"):
            return True
        # Match .next-* / .turbo-* cache variants
        if name.startswith(".next-") or name.startswith(".turbo-"):
            return True
        # Handle glob-like patterns in IGNORE_DIRS (e.g. *.egg-info)
        for pat in IGNORE_DIRS:
            if "*" in pat and Path(name).match(pat):
                return True
        return False

    # ---- 2. Count lines of code ------------------------------------
    @staticmethod
    def count_lines(filepath: Path, language: str) -> tuple[int, int, int]:
        """Returns (total, blank, comment) line counts."""
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except (PermissionError, OSError):
            return 0, 0, 0

        total = len(lines)
        blank = sum(1 for l in lines if not l.strip())
        marker = COMMENT_MARKERS.get(language)
        comment = 0
        if marker:
            for l in lines:
                s = l.strip()
                if s.startswith(marker):
                    comment += 1
        return total, blank, comment

    # ---- 3. Directory tree (top 3 levels) --------------------------
    def build_tree(self, max_levels: int = 3) -> str:
        # If focus is set, the tree starts from the focus dir
        tree_root = self.walk_root
        header = (f"{self.root.name}/{self.focus}/" if self.focus
                  else f"{self.root.name}/")
        lines: list[str] = [header]

        def _walk(path: Path, prefix: str, level: int):
            if level >= max_levels:
                return
            try:
                entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            except (PermissionError, OSError):
                return
            entries = [e for e in entries if not self._is_ignored_dir(e.name)
                       and not e.name.startswith(".")]
            for i, entry in enumerate(entries):
                is_last = (i == len(entries) - 1)
                connector = "└── " if is_last else "├── "
                label = entry.name + ("/" if entry.is_dir() else "")
                lines.append(f"{prefix}{connector}{label}")
                if entry.is_dir():
                    extension = "    " if is_last else "│   "
                    _walk(entry, prefix + extension, level + 1)

        _walk(tree_root, "", 1)
        return "\n".join(lines)

    # ---- 4. Detect git info ----------------------------------------
    def detect_git(self) -> dict:
        info: dict = {"is_git_repo": False}
        git_dir = self.root / ".git"
        if not git_dir.exists():
            return info
        info["is_git_repo"] = True

        # Branch
        head_file = git_dir / "HEAD"
        if head_file.exists():
            try:
                content = head_file.read_text().strip()
                if content.startswith("ref:"):
                    info["branch"] = content.split("refs/heads/")[-1]
                else:
                    info["branch"] = "(detached HEAD)"
                    info["commit"] = content[:7]
            except OSError:
                pass

        # Last commit (best-effort via packed-refs / COMMIT_EDITMSG)
        commit_editmsg = git_dir / "COMMIT_EDITMSG"
        if commit_editmsg.exists():
            try:
                msg = commit_editmsg.read_text(errors="ignore").strip().splitlines()
                if msg:
                    info["last_commit_msg"] = msg[0][:80]
            except OSError:
                pass

        # Remote URL
        config_file = git_dir / "config"
        if config_file.exists():
            try:
                text = config_file.read_text(errors="ignore")
                m = re.search(r'url\s*=\s*(\S+)', text)
                if m:
                    info["remote"] = m.group(1)
            except OSError:
                pass

        return info

    # ---- 5. Parse dependency files ---------------------------------
    def parse_dependencies(self) -> dict:
        """Parse ALL dependency manifests in the project (monorepo-aware).

        For monorepos with multiple package.json / requirements.txt files
        scattered across workspaces (apps/*, packages/*), each file is parsed
        and reported separately with its relative path as the key.
        """
        deps: dict = {
            "ecosystems": set(),
            "packages": {},            # rel_path -> list of pkg strings
            "workspaces": [],          # list of {path, name, is_workspace_root}
            "project_name": None,
            "project_version": None,
            "package_manager": None,   # npm | pnpm | yarn | pip | poetry | uv
        }

        # Find ALL dependency manifests (up to max_depth), already filtered by IGNORE_DIRS
        manifest_finders = [
            ("package.json", "Node.js (npm)"),
            ("requirements.txt", "Python (pip)"),
            ("pyproject.toml", "Python (PEP 518)"),
            ("go.mod", "Go module"),
            ("Cargo.toml", "Rust (Cargo)"),
        ]

        # Collect paths
        manifest_paths: dict[str, list[Path]] = {name: [] for name, _ in manifest_finders}
        for f in self.files:
            name = Path(f.rel_path).name
            if name in manifest_paths:
                manifest_paths[name].append(Path(f.abs_path))

        # Detect package manager (pnpm > yarn > npm) from lockfile presence
        if (self.root / "pnpm-lock.yaml").exists():
            deps["package_manager"] = "pnpm"
        elif (self.root / "yarn.lock").exists():
            deps["package_manager"] = "yarn"
        elif (self.root / "package-lock.json").exists():
            deps["package_manager"] = "npm"
        elif (self.root / "uv.lock").exists():
            deps["package_manager"] = "uv"
        elif (self.root / "poetry.lock").exists():
            deps["package_manager"] = "poetry"

        # ── Parse each package.json (root + workspaces) ──
        for pj_path in sorted(manifest_paths["package.json"]):
            try:
                # utf-8-sig handles BOM; some Windows tools add it to JSON files
                data = json.loads(pj_path.read_text(encoding="utf-8-sig"))
            except (json.JSONDecodeError, OSError):
                continue
            deps["ecosystems"].add("Node.js (npm)")
            rel = str(pj_path.relative_to(self.root))
            pkg_deps = []
            for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
                if isinstance(data.get(key), dict):
                    pkg_deps.extend([f"{k}@{v}" for k, v in data[key].items()])
            deps["packages"][rel] = pkg_deps

            # Detect workspace root (has "workspaces" or "pnpm" field)
            is_ws_root = ("workspaces" in data) or ("pnpm" in data and isinstance(data["pnpm"], dict) and "workspaces" in data["pnpm"])
            ws_entry = {
                "path": str(pj_path.parent.relative_to(self.root)) or ".",
                "name": data.get("name", "(unnamed)"),
                "version": data.get("version", "?"),
                "private": data.get("private", False),
                "is_workspace_root": is_ws_root,
                "dep_count": len(pkg_deps),
            }
            deps["workspaces"].append(ws_entry)

            # Top-level package.json provides project name/version
            if pj_path.parent == self.root:
                if "name" in data:
                    deps["project_name"] = data["name"]
                if "version" in data:
                    deps["project_version"] = data["version"]

        # ── Parse each requirements.txt ──
        for req_path in sorted(manifest_paths["requirements.txt"]):
            try:
                # utf-8-sig strips UTF-8 BOM if present (common on Windows-saved files)
                text = req_path.read_text(encoding="utf-8-sig", errors="ignore")
            except OSError:
                continue
            deps["ecosystems"].add("Python (pip)")
            rel = str(req_path.relative_to(self.root))
            pkgs = []
            for line in text.splitlines():
                line = line.strip()
                # Skip comments, options (-r / --), and blank lines
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                # Strip version specifiers (maxsplit=1 as keyword for Python 3.13+ compat)
                pkg = re.split(r"[=<>!~\[]", line, maxsplit=1)[0].strip()
                if pkg:
                    pkgs.append(pkg)
            deps["packages"][rel] = pkgs

        # ── Parse each pyproject.toml ──
        for pp_path in sorted(manifest_paths["pyproject.toml"]):
            try:
                # utf-8-sig strips BOM if present
                text = pp_path.read_text(encoding="utf-8-sig", errors="ignore")
            except OSError:
                continue
            deps["ecosystems"].add("Python (PEP 518)")
            rel = str(pp_path.relative_to(self.root))
            # Match dependencies = [ "pkg", ... ] (also handles multiline)
            pkgs = []
            for m in re.finditer(r'(?:^|\n)\s*(?:\[tool\.poetry\])?dependencies\s*=\s*\[([^\]]*)\]',
                                  text, re.DOTALL):
                pkgs.extend(re.findall(r'"([^"]+)"', m.group(1)))
            # Also catch PEP 508 inline table form: dependencies = { foo = "1.0" }
            if not pkgs:
                m2 = re.search(r'dependencies\s*=\s*\{([^}]*)\}', text, re.DOTALL)
                if m2:
                    pkgs.extend(re.findall(r'([a-zA-Z0-9_.-]+)\s*=', m2.group(1)))
            if pkgs:
                deps["packages"][rel] = pkgs

        # ── Parse each go.mod ──
        for gm_path in sorted(manifest_paths["go.mod"]):
            try:
                text = gm_path.read_text(errors="ignore")
            except OSError:
                continue
            deps["ecosystems"].add("Go module")
            rel = str(gm_path.relative_to(self.root))
            pkgs = []
            in_require_block = False
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("require ("):
                    in_require_block = True
                    continue
                if in_require_block and line == ")":
                    in_require_block = False
                    continue
                if in_require_block or line.startswith("require "):
                    parts = line.replace("require", "").strip().split()
                    if parts:
                        pkgs.append(parts[0])
            if pkgs:
                deps["packages"][rel] = pkgs

        # ── Parse each Cargo.toml ──
        for ct_path in sorted(manifest_paths["Cargo.toml"]):
            try:
                text = ct_path.read_text(errors="ignore")
            except OSError:
                continue
            deps["ecosystems"].add("Rust (Cargo)")
            rel = str(ct_path.relative_to(self.root))
            pkgs = re.findall(r'^\s*([a-zA-Z0-9_-]+)\s*=\s*"', text, re.MULTILINE)
            meta_keys = {"name", "version", "edition", "authors", "description",
                         "license", "repository", "homepage", "documentation",
                         "readme", "keywords", "categories", "build", "default-run"}
            pkgs = [p for p in pkgs if p not in meta_keys]
            if pkgs:
                deps["packages"][rel] = pkgs

        deps["ecosystems"] = sorted(deps["ecosystems"])
        return deps

    # ---- 6. Detect issues ------------------------------------------
    def detect_issues(self) -> list[str]:
        issues: list[str] = []

        # Missing README
        readme_variants = ["README.md", "README.rst", "README.txt", "README",
                          "readme.md", "readme.rst"]
        if not any((self.root / r).exists() for r in readme_variants):
            issues.append("No README file found — projects should have one for discoverability.")

        # Missing .gitignore
        if not (self.root / ".gitignore").exists() and (self.root / ".git").exists():
            issues.append("No .gitignore file — risk of committing build artifacts or secrets.")

        # Missing LICENSE
        license_variants = ["LICENSE", "LICENSE.md", "LICENSE.txt",
                           "COPYING", "COPYING.md", "COPYING.txt"]
        if not any((self.root / l).exists() for l in license_variants):
            issues.append("No LICENSE file — legal status of the code is unclear.")

        # ── .env files (root + nested) — potential secret leak ──
        # Read .gitignore ONCE, parse patterns, check each .env against it.
        gi = self.root / ".gitignore"
        gi_patterns: list[str] = []
        if gi.exists():
            try:
                # utf-8-sig handles BOM
                gi_patterns = [ln.strip() for ln in gi.read_text(encoding="utf-8-sig",
                                                                  errors="ignore").splitlines()
                               if ln.strip() and not ln.strip().startswith("#")]
            except OSError:
                pass

        def _is_ignored(rel_path: str, name: str) -> bool:
            """Check if a file matches any .gitignore pattern (simplified matching).

            NOTE: This is intentionally a SIMPLE matcher, not a full gitignore engine.
            It handles the most common patterns (direct name match, wildcard, full path),
            which is sufficient for the analyzer's "potential secret leak" heads-up.
            Edge cases (negation `!`, anchored `/foo`, `**/`) are not fully supported.
            When in doubt, the analyzer errs on the side of NOT flagging a file.
            """
            rel_norm = rel_path.replace("\\", "/")
            for pat in gi_patterns:
                # Skip negation patterns (we don't fully support them)
                if pat.startswith("!"):
                    continue
                # Strip leading slash (anchored patterns become relative)
                p = pat.lstrip("/")
                # Anchored pattern: only matches at root (e.g. "/.env" → only root .env)
                if pat.startswith("/") and "/" not in p:
                    # Pattern "/.env" only matches ".env" at project root
                    if p == name and "/" not in rel_norm:
                        return True
                    continue
                # Pattern with path separators: match full relative path
                if "/" in p:
                    if p == rel_norm:
                        return True
                    # Wildcard in path: e.g. "apps/*/.env"
                    if "*" in p:
                        # Convert glob to regex (simple: * → [^/]*)
                        regex = re.escape(p).replace(r"\*", r"[^/]*")
                        if re.fullmatch(regex, rel_norm):
                            return True
                    continue
                # Bare name pattern (no slash): matches that name ANYWHERE in the tree
                # e.g. ".env" matches both root .env AND apps/web/.env
                # e.g. "*.log" matches any .log file anywhere
                if "*" in p:
                    if Path(name).match(p):
                        return True
                elif p == name:
                    return True
            return False

        # Find ALL .env files in the scanned file list
        env_files_found: list[tuple[str, str]] = []  # (rel_path, name)
        for f in self.files:
            name = Path(f.rel_path).name
            # Match .env, .env.local, .env.production, .env.staging, etc.
            # but NOT .env.example or .env.sample (those are safe templates)
            if name == ".env" or (name.startswith(".env.") and not
                                  name.lower().endswith((".example", ".sample", ".template"))):
                env_files_found.append((f.rel_path, name))

        for rel_path, name in env_files_found:
            ignored_by_gitignore = _is_ignored(rel_path, name)
            # Even if .gitignore covers it, check if the file is ACTUALLY tracked by git
            # (a file committed before .gitignore was added stays tracked — that's a leak)
            tracked_by_git = self._is_git_tracked(rel_path)
            if tracked_by_git:
                issues.append(
                    f"⚠️  CRITICAL: Secret file '{rel_path}' is COMMITTED to git — "
                    f"this is an active secret leak. Remove from git with: "
                    f"git rm --cached '{rel_path}'"
                )
            elif not ignored_by_gitignore:
                issues.append(
                    f"⚠️  Secret file '{rel_path}' exists on disk but is NOT in .gitignore — "
                    f"if accidentally added, it would leak. Add '{name}' to .gitignore."
                )

        # ── Backup files (*.backup, *.bak, *.orig, *.old, *.backup_*) ──
        # CONSERVATIVE POLICY: Only flag files with EXPLICIT backup markers in their name.
        # This avoids false positives on:
        #   - Timestamped reports (analysis_report_20260712_155215.json — even if
        #     a parent analysis_report.json exists, they're independent runs, not backups)
        #   - Sequential logs in reports/, output/, logs/ directories
        #
        # Matches:
        #   file.bak, file.backup, file.orig, file.old, file.save, file.swp, file.tmp
        #   file.py.backup_auth, file.py.backup_fix, file.py.backup_force
        #   file.py.backup_20260714_072112 (named backup with timestamp)
        backup_exts = (".backup", ".bak", ".orig", ".old", ".save", ".swp", ".tmp")
        # Directories where timestamped files are expected (extra safety filter)
        output_dirs = {"reports", "output", "outputs", "logs", "log",
                       "analysis_reports", "analysis_report", "audit",
                       "build_logs", "test_results", "coverage"}
        backup_files: list[str] = []
        for f in self.files:
            name = Path(f.rel_path).name
            lower_name = name.lower()
            rel_dir = str(Path(f.rel_path).parent).replace("\\", "/")

            # Skip files in known output/report/log directories entirely
            # (timestamped files there are expected, not backups — even with .bak)
            # Actually NO: a .bak in reports/ IS still a backup. Let me not skip
            # these — instead, only skip the *timestamp heuristic* for these dirs.
            # Keep all explicit-extension matches.

            is_backup = False
            # 1. Classic backup extensions at end of filename
            if any(lower_name.endswith(ext) for ext in backup_exts):
                is_backup = True
            # 2. Named backups: file.py.backup_auth, file.py.backup_fix,
            #    file.py.backup_20260714_072112 (anything after .backup)
            elif ".backup" in lower_name:
                idx = lower_name.find(".backup")
                suffix = lower_name[idx:]
                # Valid: .backup, .backup_X, .backup_X_Y, .backup_TIMESTAMP
                if re.match(r'\.backup(_[a-z0-9_]+)?$', suffix):
                    is_backup = True
            # NOTE: We intentionally do NOT flag plain timestamped files like
            # `analysis_report_20260712_155215.json` even if a parent file exists,
            # because that pattern commonly represents independent report runs
            # (not backups). Real backups always have an explicit `.backup`/`.bak`
            # marker in their name.

            if is_backup:
                backup_files.append(f.rel_path)

        if backup_files:
            issues.append(
                f"Found {len(backup_files)} backup file(s) in the repo — "
                f"git history is the source of truth; remove these to reduce noise. "
                f"Examples: {', '.join(backup_files[:5])}"
                + (f" (and {len(backup_files) - 5} more)" if len(backup_files) > 5 else "")
            )

        # ── Database files in repo (*.db, *.sqlite, *.sqlite3) ──
        db_files: list[str] = []
        db_exts = (".db", ".sqlite", ".sqlite3", ".db-journal", ".db-wal", ".db-shm")
        for f in self.files:
            name = Path(f.rel_path).name
            if any(name.lower().endswith(ext) for ext in db_exts):
                db_files.append(f.rel_path)
        if db_files:
            issues.append(
                f"⚠️  Found {len(db_files)} database file(s) committed to the repo — "
                f"these may contain user data and should be in .gitignore, not in git. "
                f"Files: {', '.join(db_files)}"
            )

        # ── Oversized source files (>5MB, excluding common binary types) ──
        for f in self.files:
            if f.size > 5 * 1024 * 1024:
                if f.ext not in {".png", ".jpg", ".jpeg", ".gif", ".mp4",
                                 ".mov", ".zip", ".tar", ".gz", ".pdf",
                                 ".woff", ".woff2", ".ttf", ".otf",
                                 ".safetensors", ".bin", ".pt", ".onnx", ".h5", ".keras",
                                 ".msgpack", ".pkl", ".npy", ".npz", ".parquet"}:
                    issues.append(f"Large source file ({f.size / 1024 / 1024:.1f} MB): "
                                  f"{f.rel_path}")

        # ── Large ML model files (specific heads-up) ──
        ml_exts = {".safetensors", ".bin", ".pt", ".onnx", ".h5", ".keras", ".pkl"}
        ml_files = [f for f in self.files if f.ext in ml_exts and f.size > 1 * 1024 * 1024]
        if ml_files:
            issues.append(
                f"Found {len(ml_files)} ML model file(s) > 1MB in the repo — "
                f"consider Git LFS or a download script instead. "
                f"Largest: {ml_files[0].rel_path} "
                f"({self._human_size(ml_files[0].size)})"
            )

        # ── If the project has source code but no test files ──
        if self.files and not any(self._is_test_file(f.rel_path) for f in self.files):
            issues.append("No test files detected — consider adding tests.")

        return issues

    @staticmethod
    def _is_test_file(rel_path: str) -> bool:
        name = Path(rel_path).name
        return any(re.match(p, name, re.IGNORECASE) for p in TEST_PATTERNS) \
            or "__tests__" in rel_path \
            or "/tests/" in rel_path.replace("\\", "/") \
            or "/test/" in rel_path.replace("\\", "/")

    def _is_git_tracked(self, rel_path: str) -> bool:
        """Check if a file is tracked by git (committed to the repo).

        Uses `git ls-files` which lists all tracked files. Falls back to
        False if git is unavailable or the path is not a git repo.
        """
        if not hasattr(self, "_git_tracked_cache"):
            git_dir = self.root / ".git"
            if not git_dir.exists():
                self._git_tracked_cache = set()
            else:
                import subprocess
                try:
                    result = subprocess.run(
                        ["git", "ls-files"],
                        cwd=str(self.root),
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if result.returncode == 0:
                        # Normalize paths to forward slashes for cross-platform compare
                        self._git_tracked_cache = {
                            line.strip().replace("\\", "/")
                            for line in result.stdout.splitlines()
                            if line.strip()
                        }
                    else:
                        self._git_tracked_cache = set()
                except (subprocess.SubprocessError, FileNotFoundError, OSError):
                    self._git_tracked_cache = set()
        # Normalize input path the same way
        return rel_path.replace("\\", "/") in self._git_tracked_cache

    # ---- 7. Build full report --------------------------------------
    def analyze(self) -> ProjectReport:
        self.walk()

        report = ProjectReport(
            root=str(self.root),
            analyzed_at=datetime.now().isoformat(timespec="seconds"),
            focus=self.focus,
        )
        report.total_files = len(self.files)
        report.total_size_bytes = sum(f.size for f in self.files)
        report.directory_tree = self.build_tree()
        report.git_info = self.detect_git()
        report.errors = self.errors

        # Files & LOC by language
        files_by_lang: Counter = Counter()
        loc_by_lang: Counter = Counter()
        for f in self.files:
            if f.language:
                files_by_lang[f.language] += 1
                if self.count_loc:
                    total, _, _ = self.count_lines(Path(f.abs_path), f.language)
                    loc_by_lang[f.language] += total
                    report.total_loc += total

        report.files_by_language = dict(files_by_lang.most_common())
        report.loc_by_language = dict(loc_by_lang.most_common())

        # Largest files (top 10)
        sorted_by_size = sorted(self.files, key=lambda f: f.size, reverse=True)[:10]
        report.largest_files = [
            {"path": f.rel_path, "size_bytes": f.size,
             "size_human": self._human_size(f.size)}
            for f in sorted_by_size
        ]

        # Detected config files
        detected: dict = {}
        for f in self.files:
            name = Path(f.rel_path).name
            # Match exact config name, or special-cased patterns
            if name in CONFIG_FILES:
                detected[f.rel_path] = CONFIG_FILES[name]
            elif name.lower() == "dockerfile":
                detected[f.rel_path] = "Docker container"
            elif name.lower() == "makefile":
                detected[f.rel_path] = "Make build"
            elif name.lower() == "jenkinsfile":
                detected[f.rel_path] = "Jenkins CI"
            elif name.lower() in {"license", "license.md", "license.txt"}:
                detected[f.rel_path] = "License file"
            elif name.lower() in {"readme.md", "readme.rst", "readme.txt", "readme"}:
                detected[f.rel_path] = "README documentation"
            elif ".github" in f.rel_path and f.ext in {".yml", ".yaml"}:
                detected[f.rel_path] = "GitHub Actions CI"
                report.ci_cd.append(f.rel_path)
            elif name == ".gitlab-ci.yml":
                detected[f.rel_path] = "GitLab CI"
                report.ci_cd.append(f.rel_path)
            elif name == "Jenkinsfile":
                detected[f.rel_path] = "Jenkins CI"
                report.ci_cd.append(f.rel_path)

        report.detected_configs = detected

        # Entry points — top-level files OR files under the focus dir OR
        # files under common monorepo dirs (apps/, packages/, etc.)
        focus_parts = tuple(self.focus.split("/")) if self.focus else ()
        monorepo_dirs = {"apps", "packages", "src", "backend", "frontend",
                         "server", "services"}
        for f in self.files:
            rel = Path(f.rel_path)
            parts = rel.parts
            # Case A: file directly under project root
            if len(parts) == 1 and rel.name in ENTRY_POINT_NAMES:
                report.entry_points.append(f.rel_path)
            # Case B: file directly under focus dir OR under any subdirectory of focus
            # (e.g. focus="apps", file="apps/api/main.py" or "apps/main.py")
            elif (focus_parts
                  and len(parts) > len(focus_parts)
                  and parts[:len(focus_parts)] == focus_parts
                  and rel.name in ENTRY_POINT_NAMES):
                report.entry_points.append(f.rel_path)
            # Case C: file under apps/, packages/, etc. — depth 2 or 3
            # (covers apps/main.py AND apps/api/main.py AND packages/web/index.ts)
            elif (not focus_parts and len(parts) in (2, 3)
                  and parts[0] in monorepo_dirs
                  and rel.name in ENTRY_POINT_NAMES):
                report.entry_points.append(f.rel_path)

        # Docker files
        report.docker_files = [
            f.rel_path for f in self.files
            if f.rel_path.lower().endswith("dockerfile")
            or "docker-compose" in f.rel_path.lower()
            or Path(f.rel_path).name.lower() == "dockerfile"
        ]

        # Test files
        report.test_files = [f.rel_path for f in self.files if self._is_test_file(f.rel_path)]

        # Documentation files
        report.doc_files = [
            f.rel_path for f in self.files
            if f.ext in DOC_EXTENSIONS
            or Path(f.rel_path).name.lower().startswith("readme")
        ]

        # Dependencies
        report.dependencies = self.parse_dependencies()

        # Issues
        report.issues = self.detect_issues()

        return report

    @staticmethod
    def _human_size(n: int) -> str:
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} PB"


# ─────────────────────────────────────────────────────────────────────
# REPORT FORMATTERS
# ─────────────────────────────────────────────────────────────────────

def format_text_report(r: ProjectReport) -> str:
    """Render the ProjectReport as a human-readable text block."""
    out: list[str] = []
    bar = "═" * 70

    out.append(bar)
    out.append("  PROJECT ANALYSIS REPORT  |  گزارش تحلیل پروژه")
    out.append(bar)
    out.append(f"  Root path      : {r.root}")
    if r.focus:
        out.append(f"  Focus subdir   : {r.focus}/  (monorepo mode — only this subdir is walked)")
    out.append(f"  Analyzed at    : {r.analyzed_at}")
    out.append(f"  Total files    : {r.total_files:,}")
    out.append(f"  Total size     : {ProjectAnalyzer._human_size(r.total_size_bytes)}")
    if r.total_loc:
        out.append(f"  Total LOC      : {r.total_loc:,}")
    if r.errors:
        out.append(f"  Access errors  : {len(r.errors)} (see end of report)")
    out.append("")

    # ── Git info
    if r.git_info.get("is_git_repo"):
        out.append("─" * 70)
        out.append("  1. VERSION CONTROL  |  کنترل نسخه")
        out.append("─" * 70)
        out.append(f"  Branch          : {r.git_info.get('branch', '(unknown)')}")
        if r.git_info.get("commit"):
            out.append(f"  HEAD commit     : {r.git_info['commit']}")
        if r.git_info.get("last_commit_msg"):
            out.append(f"  Last commit     : {r.git_info['last_commit_msg']}")
        if r.git_info.get("remote"):
            out.append(f"  Remote          : {r.git_info['remote']}")
        out.append("")

    # ── Directory tree
    out.append("─" * 70)
    out.append("  2. DIRECTORY TREE (top 3 levels, hidden/generated dirs excluded)")
    out.append("─" * 70)
    out.append(r.directory_tree)
    out.append("")

    # ── Languages
    out.append("─" * 70)
    out.append("  3. LANGUAGE DISTRIBUTION  |  توزیع زبان‌ها")
    out.append("─" * 70)
    if r.files_by_language:
        out.append(f"  {'Language':<28} {'Files':>8} {'LOC':>12}")
        out.append(f"  {'-'*28} {'-'*8} {'-'*12}")
        for lang, cnt in r.files_by_language.items():
            loc = r.loc_by_language.get(lang, 0)
            loc_str = f"{loc:,}" if loc else "—"
            out.append(f"  {lang:<28} {cnt:>8} {loc_str:>12}")
    else:
        out.append("  (no recognized source files found)")
    out.append("")

    # ── Detected configs / tech stack
    out.append("─" * 70)
    out.append("  4. DETECTED TECH STACK  |  پشته فنی شناسایی‌شده")
    out.append("─" * 70)
    if r.detected_configs:
        # Group by category
        grouped: dict = defaultdict(list)
        for path, desc in r.detected_configs.items():
            grouped[desc].append(path)
        for desc, paths in sorted(grouped.items()):
            out.append(f"  • {desc}")
            for p in paths[:3]:  # show up to 3 paths per category
                out.append(f"      └─ {p}")
            if len(paths) > 3:
                out.append(f"      └─ ... and {len(paths) - 3} more")
    else:
        out.append("  (no recognized config files found)")
    out.append("")

    # ── Dependencies
    out.append("─" * 70)
    out.append("  5. DEPENDENCIES  |  وابستگی‌ها" + ("  (monorepo — all workspaces)" if r.dependencies.get("workspaces") else ""))
    out.append("─" * 70)
    if r.dependencies.get("ecosystems"):
        out.append(f"  Ecosystems      : {', '.join(r.dependencies['ecosystems'])}")
        if r.dependencies.get("package_manager"):
            out.append(f"  Package manager : {r.dependencies['package_manager']}")
        if r.dependencies.get("project_name"):
            out.append(f"  Project name    : {r.dependencies['project_name']}")
        if r.dependencies.get("project_version"):
            out.append(f"  Project version : {r.dependencies['project_version']}")

        # Workspaces (monorepo)
        workspaces = r.dependencies.get("workspaces", [])
        if workspaces:
            out.append("")
            out.append(f"  Workspaces ({len(workspaces)} found):")
            out.append(f"  {'Workspace path':<30} {'Name':<28} {'Deps':>5} {'Type':<14}")
            out.append(f"  {'-'*30} {'-'*28} {'-'*5} {'-'*14}")
            for ws in workspaces:
                ws_type = "workspace root" if ws.get("is_workspace_root") else "package"
                if ws.get("private"):
                    ws_type += " (private)"
                out.append(f"  {ws['path']:<30} {ws['name']:<28} {ws['dep_count']:>5} {ws_type:<14}")

        out.append("")
        # Per-manifest packages
        for source, pkgs in r.dependencies.get("packages", {}).items():
            out.append(f"  [{source}] ({len(pkgs)} packages)")
            for p in pkgs[:15]:
                out.append(f"    • {p}")
            if len(pkgs) > 15:
                out.append(f"    • ... and {len(pkgs) - 15} more")
            out.append("")
    else:
        out.append("  (no recognized dependency manifests found)")
        out.append("")

    # ── Entry points
    out.append("─" * 70)
    out.append("  6. ENTRY POINTS  |  نقاط ورود")
    out.append("─" * 70)
    if r.entry_points:
        for ep in r.entry_points:
            out.append(f"  → {ep}")
    else:
        out.append("  (no standard entry points found in root directory)")
    out.append("")

    # ── Test files
    out.append("─" * 70)
    out.append("  7. TEST FILES  |  فایل‌های تست")
    out.append("─" * 70)
    if r.test_files:
        out.append(f"  Found {len(r.test_files)} test file(s):")
        for t in r.test_files[:20]:
            out.append(f"  • {t}")
        if len(r.test_files) > 20:
            out.append(f"  • ... and {len(r.test_files) - 20} more")
    else:
        out.append("  No test files detected.")
    out.append("")

    # ── Documentation
    out.append("─" * 70)
    out.append("  8. DOCUMENTATION  |  مستندات")
    out.append("─" * 70)
    if r.doc_files:
        for d in r.doc_files[:15]:
            out.append(f"  📄 {d}")
        if len(r.doc_files) > 15:
            out.append(f"  ... and {len(r.doc_files) - 15} more")
    else:
        out.append("  No documentation files found.")
    out.append("")

    # ── CI/CD
    out.append("─" * 70)
    out.append("  9. CI/CD CONFIGURATION  |  پیکربندی CI/CD")
    out.append("─" * 70)
    if r.ci_cd:
        for c in r.ci_cd:
            out.append(f"  • {c}")
    else:
        out.append("  No CI/CD configuration detected.")
    out.append("")

    # ── Docker
    out.append("─" * 70)
    out.append(" 10. DOCKER / CONTAINERIZATION")
    out.append("─" * 70)
    if r.docker_files:
        for d in r.docker_files:
            out.append(f"  • {d}")
    else:
        out.append("  No Docker files detected.")
    out.append("")

    # ── Largest files
    out.append("─" * 70)
    out.append(" 11. LARGEST FILES (top 10)")
    out.append("─" * 70)
    for f in r.largest_files:
        out.append(f"  {f['size_human']:>10}  {f['path']}")
    out.append("")

    # ── Issues
    out.append("─" * 70)
    out.append(" 12. ISSUES & RECOMMENDATIONS  |  مسائل و پیشنهادات")
    out.append("─" * 70)
    if r.issues:
        for i, issue in enumerate(r.issues, 1):
            out.append(f"  {i}. {issue}")
    else:
        out.append("  No issues detected. ✅")
    out.append("")

    # ── Errors
    if r.errors:
        out.append("─" * 70)
        out.append(" ACCESS ERRORS (files that could not be read)")
        out.append("─" * 70)
        for e in r.errors[:20]:
            out.append(f"  ! {e}")
        if len(r.errors) > 20:
            out.append(f"  ... and {len(r.errors) - 20} more")
        out.append("")

    out.append(bar)
    out.append("  End of report")
    out.append(bar)
    return "\n".join(out)


# ─────────────────────────────────────────────────────────────────────
# CLI ENTRY POINT
# ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="project_analyzer",
        description="Analyze a software project directory and produce a comprehensive report.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the project directory (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the report as JSON instead of text",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=12,
        help="Maximum directory depth to scan (default: 12)",
    )
    parser.add_argument(
        "--no-loc",
        action="store_true",
        help="Skip line-of-code counting (faster for large projects)",
    )
    parser.add_argument(
        "--focus",
        type=str,
        default=None,
        help="Focus analysis on a subdirectory (e.g. 'apps' or 'packages/web'). "
             "Git/config detection still uses the project root; the file walk, "
             "language stats, and tree are scoped to this subdir. Useful for monorepos.",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Write the report to this file (default: print to stdout)",
    )
    args = parser.parse_args()

    root = Path(args.path).expanduser().resolve()
    if not root.exists():
        print(f"Error: path does not exist: {root}", file=sys.stderr)
        sys.exit(1)
    if not root.is_dir():
        print(f"Error: not a directory: {root}", file=sys.stderr)
        sys.exit(1)

    # Validate focus subdir if provided
    focus = args.focus.strip().strip("/\\") if args.focus else None
    if focus:
        focus_path = (root / focus).resolve()
        if not focus_path.exists():
            print(f"Error: focus subdir does not exist: {focus_path}", file=sys.stderr)
            sys.exit(1)
        if not focus_path.is_dir():
            print(f"Error: focus path is not a directory: {focus_path}", file=sys.stderr)
            sys.exit(1)

    analyzer = ProjectAnalyzer(root, max_depth=args.depth, count_loc=not args.no_loc, focus=focus)
    try:
        report = analyzer.analyze()
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        # Convert dataclass to dict; sets already converted to lists by parse_dependencies
        output = asdict(report)
        text = json.dumps(output, indent=2, ensure_ascii=False, default=str)
    else:
        text = format_text_report(report)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Report written to: {args.output}", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()
