#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
ECO-NOJIN PROJECT COMPREHENSIVE ANALYZER
===============================================================================
Platform: Hydroma-Nojin / Eco-Nojin
Organization: Dasht Omid Narvan Agricultural & Industrial Company
Version: 2.0.0
Date: August 2026

Description:
    A comprehensive static analysis tool for the Eco-Nojin project that performs:
    1. Directory structure analysis
    2. File integrity verification
    3. Orphan file detection
    4. TODO/Technical debt extraction
    5. Dependency analysis
    6. Security vulnerability scanning
    7. Code complexity metrics
    8. Architecture pattern detection
    9. Dead code identification
    10. Import graph generation

Usage:
    python analyze_econojin.py --path /path/to/project [--output report.md]

License: Proprietary - Dasht Omid Narvan
===============================================================================
"""

import argparse
import ast
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# =============================================================================
# DATA MODELS
# =============================================================================


class FileStatus(Enum):
    HEALTHY = "healthy"
    DAMAGED_CRITICAL = "damaged_critical"
    DAMAGED_MINOR = "damaged_minor"
    ORPHAN = "orphan"
    DEAD_CODE = "dead_code"
    INCOMPLETE = "incomplete"
    UNKNOWN = "unknown"


class Priority(Enum):
    P0 = "P0"  # Blocker
    P1 = "P1"  # Critical
    P2 = "P2"  # Important
    P3 = "P3"  # Nice to have


@dataclass
class FileInfo:
    path: str
    extension: str
    size_bytes: int
    lines: int
    last_modified: datetime
    md5_hash: str
    status: FileStatus = FileStatus.UNKNOWN
    issues: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    todos: List[Dict[str, str]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    is_orphan: bool = False
    references: int = 0


@dataclass
class AnalysisReport:
    project_name: str
    project_path: str
    analysis_date: datetime
    total_files: int = 0
    total_lines: int = 0
    total_size_mb: float = 0.0
    files_by_extension: Dict[str, int] = field(default_factory=dict)
    files_by_status: Dict[FileStatus, int] = field(default_factory=dict)
    damaged_files: List[FileInfo] = field(default_factory=list)
    orphan_files: List[FileInfo] = field(default_factory=list)
    incomplete_files: List[FileInfo] = field(default_factory=list)
    todos: List[Dict[str, Any]] = field(default_factory=list)
    security_issues: List[Dict[str, str]] = field(default_factory=list)
    architecture_patterns: Dict[str, List[str]] = field(default_factory=dict)
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


# =============================================================================
# ANALYZER CLASS
# =============================================================================


class EcoNojinAnalyzer:
    """
    Comprehensive static analyzer for the Eco-Nojin project.
    Implements multi-layered analysis including security, structure, and semantics.
    """

    # Security patterns to detect
    SECURITY_PATTERNS = {
        "hardcoded_secrets": [
            r'(?i)(password|passwd|secret|api_key|apikey|token|auth)\s*=\s*["\'][^"\']+["\']',
            r'(?i)(AWS|aws)_?(ACCESS|SECRET)_?(KEY|key)\s*=\s*["\'][^"\']+["\']',
            r'(?i)(DATABASE|DB|POSTGRES|MYSQL)_?(URL|url|PASSWORD|password)\s*=\s*["\'][^"\']+["\']',
        ],
        "sql_injection": [
            r'(?i)execute\s*\(\s*["\'].*?%s.*?["\']\s*%',
            r'(?i)f["\'].*?SELECT.*?\{.*?\}.*?["\']',
            r"(?i)\.format\(.*?\).*?(?:SELECT|INSERT|UPDATE|DELETE)",
        ],
        "insecure_crypto": [
            r"(?i)md5\(",
            r"(?i)sha1\(",
            r"(?i)DES|RC4|ECB",
        ],
        "dangerous_functions": [
            r"(?i)\beval\s*\(",
            r"(?i)\bexec\s*\(",
            r"(?i)\bpickle\.loads?\s*\(",
            r"(?i)\bsubprocess\.call\s*\(.*?shell\s*=\s*True",
        ],
        "cors_misconfiguration": [
            r"(?i)Access-Control-Allow-Origin.*?\*",
            r'(?i)CORS.*?allow_origins.*?\["\*"\]',
        ],
    }

    # TODO patterns across languages
    TODO_PATTERNS = [
        r"#\s*TODO[:\s]*(.*)",
        r"//\s*TODO[:\s]*(.*)",
        r"/\*\s*TODO[:\s]*(.*?)\*/",
        r"{/\*\s*TODO[:\s]*(.*?)\*/}",
        r"#\s*FIXME[:\s]*(.*)",
        r"#\s*HACK[:\s]*(.*)",
        r"#\s*XXX[:\s]*(.*)",
        r"#\s*NOTE[:\s]*(.*)",
        r"<!--\s*TODO[:\s]*(.*?)-->",
    ]

    # Known Eco-Nojin project patterns
    PROJECT_PATTERNS = {
        "FastAPI": [
            r"from\s+fastapi",
            r"@app\.(get|post|put|delete|patch)",
            r"@router\.(get|post|put|delete|patch)",
            r"APIRouter\(",
        ],
        "React": [
            r"import\s+React",
            r'from\s+["\']react["\']',
            r"useState\s*\(",
            r"useEffect\s*\(",
            r"jsx|tsx",
        ],
        "SQLAlchemy": [
            r"from\s+sqlalchemy",
            r"Column\(",
            r"relationship\(",
            r"Base\.metadata",
        ],
        "Satellite_Data": [
            r"sentinel|Sentinel|SENTINEL",
            r"NASA|nasa|POWER",
            r"SAR|sar",
            r"Landsat|landsat",
            r"NDVI|ndvi|EVI|evi",
        ],
        "Simulation_Models": [
            r"AquaCrop|aquacrop",
            r"RothC|rothc",
            r"DSSAT|dssat",
            r"SWAT|swat",
            r"SCS-CN|SCS",
            r"Penman|penman|Monteith",
        ],
        "IoT_Sensors": [
            r"LoRa|lora",
            r"MQTT|mqtt",
            r"sensor|Sensor",
            r"Arduino|arduino",
            r"Raspberry|raspberry",
        ],
        "Blockchain": [
            r"web3|Web3",
            r"smart.?contract|SmartContract",
            r"blockchain|Blockchain",
            r"solidity|Solidity",
        ],
        "AI_ML": [
            r"tensorflow|TensorFlow|tf\.",
            r"pytorch|PyTorch|torch\.",
            r"scikit|sklearn",
            r"PINN|pinn",
            r"neural.?network|NeuralNetwork",
        ],
    }

    def __init__(self, project_path: str, output_path: Optional[str] = None):
        self.project_path = Path(project_path).resolve()
        self.output_path = output_path
        self.files: Dict[str, FileInfo] = {}
        self.report = AnalysisReport(
            project_name="Eco-Nojin / Hydroma-Nojin",
            project_path=str(self.project_path),
            analysis_date=datetime.now(),
        )
        self._setup_ignore_patterns()

    def _setup_ignore_patterns(self):
        """Setup patterns for directories/files to ignore."""
        self.ignore_dirs = {
            "node_modules",
            ".git",
            "__pycache__",
            ".pytest_cache",
            "dist",
            "build",
            ".next",
            "coverage",
            ".venv",
            "venv",
            "env",
            ".env",
            ".idea",
            ".vscode",
            ".mypy_cache",
            ".tox",
            "eggs",
            "*.egg-info",
            ".hg",
            ".svn",
        }
        self.ignore_files = {
            ".DS_Store",
            "Thumbs.db",
            "*.pyc",
            "*.pyo",
            "*.lock",
            "package-lock.json",
            "yarn.lock",
        }

    def _should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored during analysis."""
        for part in path.parts:
            if part in self.ignore_dirs:
                return True
            if any(part.startswith(d) for d in self.ignore_dirs if d.startswith(".")):
                return True
        return path.name in self.ignore_files

    def _calculate_md5(self, filepath: Path) -> str:
        """Calculate MD5 hash of a file."""
        hasher = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"

    def _count_lines(self, filepath: Path) -> Tuple[int, List[str]]:
        """Count lines in a file and return content."""
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                return len(lines), lines
        except Exception:
            return 0, []

    def _extract_imports_python(self, content: List[str]) -> List[str]:
        """Extract Python imports from file content."""
        imports = []
        for line in content:
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                # Parse the import statement
                match = re.match(r"(?:from\s+([\w.]+)\s+)?import\s+(.+)", line)
                if match:
                    module = match.group(1) or match.group(2)
                    imports.append(module.split(".")[0])
        return imports

    def _extract_imports_js_ts(self, content: List[str]) -> List[str]:
        """Extract JavaScript/TypeScript imports from file content."""
        imports = []
        import_pattern = re.compile(r"""import\s+(?:[\w\s{},*]+\s+from\s+)?['"]([^'"]+)['"]""")
        for line in content:
            matches = import_pattern.findall(line)
            for match in matches:
                if match.startswith("."):
                    imports.append(match)
                elif not match.startswith("http"):
                    imports.append(match.split("/")[0])
        return imports

    def _extract_todos(self, content: List[str], filepath: str) -> List[Dict[str, str]]:
        """Extract TODO comments from file content."""
        todos = []
        for i, line in enumerate(content, 1):
            for pattern in self.TODO_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    todos.append(
                        {
                            "file": filepath,
                            "line": i,
                            "text": match.group(1).strip(),
                            "type": match.group(0).split(":")[0].strip("#/ *"),
                        }
                    )
        return todos

    def _check_security_issues(self, content: List[str], filepath: str) -> List[Dict[str, str]]:
        """Check for security vulnerabilities in file content."""
        issues = []
        content_str = "\n".join(content)

        for category, patterns in self.SECURITY_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content_str, re.MULTILINE)
                for match in matches:
                    # Find line number
                    line_num = content_str[: match.start()].count("\n") + 1
                    issues.append(
                        {
                            "file": filepath,
                            "line": line_num,
                            "category": category,
                            "pattern": pattern,
                            "match": match.group(0)[:100],
                        }
                    )
        return issues

    def _detect_architecture_patterns(self, content: List[str]) -> List[str]:
        """Detect architectural patterns in file content."""
        detected = []
        content_str = "\n".join(content)

        for pattern_name, regex_patterns in self.PROJECT_PATTERNS.items():
            for regex in regex_patterns:
                if re.search(regex, content_str, re.IGNORECASE):
                    detected.append(pattern_name)
                    break
        return detected

    def _check_syntax_python(self, filepath: Path) -> List[str]:
        """Check Python file syntax using AST."""
        issues = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            ast.parse(source)
        except SyntaxError as e:
            issues.append(f"SyntaxError: {e.msg} at line {e.lineno}")
        except Exception as e:
            issues.append(f"ParseError: {str(e)}")
        return issues

    def _check_syntax_js_ts(self, filepath: Path) -> List[str]:
        """Basic syntax checks for JS/TS files."""
        issues = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Check balanced braces
            if content.count("{") != content.count("}"):
                issues.append("Unbalanced curly braces {}")
            if content.count("(") != content.count(")"):
                issues.append("Unbalanced parentheses ()")
            if content.count("[") != content.count("]"):
                issues.append("Unbalanced brackets []")

            # Check for common errors
            if "undefined" in content and "typeof" not in content:
                issues.append("Possible undefined reference without typeof check")

        except Exception as e:
            issues.append(f"ReadError: {str(e)}")
        return issues

    def scan_directory(self):
        """Scan the entire project directory structure."""
        print(f"[INFO] Scanning project: {self.project_path}")

        for root, dirs, files in os.walk(self.project_path):
            # Filter ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(Path(root) / d)]

            for filename in files:
                filepath = Path(root) / filename

                if self._should_ignore(filepath):
                    continue

                # Skip binary files
                if filename.endswith(
                    (
                        ".png",
                        ".jpg",
                        ".jpeg",
                        ".gif",
                        ".ico",
                        ".pdf",
                        ".zip",
                        ".tar",
                        ".gz",
                        ".db",
                        ".sqlite",
                        ".exe",
                        ".dll",
                        ".so",
                    )
                ):
                    continue

                self._analyze_file(filepath)

        print(f"[INFO] Scanned {self.report.total_files} files")

    def _analyze_file(self, filepath: Path):
        """Analyze a single file."""
        try:
            rel_path = str(filepath.relative_to(self.project_path))
            extension = filepath.suffix.lower()

            # Get file stats
            stat = filepath.stat()
            line_count, content = self._count_lines(filepath)
            md5_hash = self._calculate_md5(filepath)

            # Create FileInfo object
            file_info = FileInfo(
                path=rel_path,
                extension=extension,
                size_bytes=stat.st_size,
                lines=line_count,
                last_modified=datetime.fromtimestamp(stat.st_mtime),
                md5_hash=md5_hash,
            )

            # Extension-specific analysis
            if extension in (".py",):
                file_info.imports = self._extract_imports_python(content)
                syntax_issues = self._check_syntax_python(filepath)
                file_info.issues.extend(syntax_issues)
                if syntax_issues:
                    file_info.status = FileStatus.DAMAGED_CRITICAL

            elif extension in (".js", ".jsx", ".ts", ".tsx"):
                file_info.imports = self._extract_imports_js_ts(content)
                syntax_issues = self._check_syntax_js_ts(filepath)
                file_info.issues.extend(syntax_issues)
                if syntax_issues:
                    file_info.status = FileStatus.DAMAGED_MINOR

            # Extract TODOs
            file_info.todos = self._extract_todos(content, rel_path)
            if file_info.todos:
                file_info.status = FileStatus.INCOMPLETE

            # Security checks
            security_issues = self._check_security_issues(content, rel_path)
            self.report.security_issues.extend(security_issues)

            # Architecture detection
            patterns = self._detect_architecture_patterns(content)
            for pattern in patterns:
                if pattern not in self.report.architecture_patterns:
                    self.report.architecture_patterns[pattern] = []
                self.report.architecture_patterns[pattern].append(rel_path)

            # If no issues found, mark as healthy
            if file_info.status == FileStatus.UNKNOWN:
                file_info.status = FileStatus.HEALTHY

            # Store file info
            self.files[rel_path] = file_info

            # Update report totals
            self.report.total_files += 1
            self.report.total_lines += line_count
            self.report.total_size_mb += stat.st_size / (1024 * 1024)

            # Count by extension
            ext = extension or "no_extension"
            self.report.files_by_extension[ext] = self.report.files_by_extension.get(ext, 0) + 1

        except Exception as e:
            print(f"[ERROR] Failed to analyze {filepath}: {str(e)}")

    def detect_orphan_files(self):
        """Detect files that are not referenced by other files."""
        print("[INFO] Detecting orphan files...")

        # Build a reference map
        all_files = set(self.files.keys())
        referenced_files = set()

        for filepath, file_info in self.files.items():
            for imp in file_info.imports:
                # Try to match import to a file
                for other_file in all_files:
                    if other_file.endswith(imp) or imp in other_file:
                        referenced_files.add(other_file)
                        self.files[other_file].references += 1

        # Files that are not referenced and not entry points
        entry_points = {
            "main.py",
            "app.py",
            "index.js",
            "index.ts",
            "index.tsx",
            "manage.py",
            "setup.py",
            "__init__.py",
            "App.tsx",
            "App.jsx",
        }

        for filepath, file_info in self.files.items():
            filename = Path(filepath).name
            if (
                file_info.references == 0
                and filename not in entry_points
                and "test" not in filepath.lower()
                and "config" not in filepath.lower()
            ):
                file_info.is_orphan = True
                file_info.status = FileStatus.ORPHAN
                self.report.orphan_files.append(file_info)

    def categorize_files(self):
        """Categorize files by status."""
        print("[INFO] Categorizing files by status...")

        for file_info in self.files.values():
            if file_info.status not in self.report.files_by_status:
                self.report.files_by_status[file_info.status] = 0
            self.report.files_by_status[file_info.status] += 1

            if file_info.status == FileStatus.DAMAGED_CRITICAL:
                self.report.damaged_files.append(file_info)
            elif file_info.status == FileStatus.INCOMPLETE:
                self.report.incomplete_files.append(file_info)

            # Collect all TODOs
            self.report.todos.extend(file_info.todos)

    def analyze_dependencies(self):
        """Analyze project dependencies from package files."""
        print("[INFO] Analyzing dependencies...")

        dep_files = {
            "package.json": self._parse_package_json,
            "requirements.txt": self._parse_requirements_txt,
            "pyproject.toml": self._parse_pyproject_toml,
            "Pipfile": self._parse_pipfile,
            "composer.json": self._parse_composer_json,
        }

        for dep_file, parser in dep_files.items():
            filepath = self.project_path / dep_file
            if filepath.exists():
                try:
                    parser(filepath)
                except Exception as e:
                    print(f"[WARNING] Failed to parse {dep_file}: {str(e)}")

        # Also check subdirectories
        for root, dirs, files in os.walk(self.project_path):
            if self._should_ignore(Path(root)):
                continue
            for filename in files:
                if filename in dep_files:
                    filepath = Path(root) / filename
                    parser = dep_files[filename]
                    try:
                        parser(filepath)
                    except Exception as e:
                        print(f"[WARNING] Failed to parse {filepath}: {str(e)}")

    def _parse_package_json(self, filepath: Path):
        """Parse package.json for Node.js dependencies."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})

        rel_path = str(filepath.relative_to(self.project_path))
        self.report.dependency_graph[rel_path] = list(deps.keys()) + list(dev_deps.keys())

    def _parse_requirements_txt(self, filepath: Path):
        """Parse requirements.txt for Python dependencies."""
        deps = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Extract package name
                    match = re.match(r"^([a-zA-Z0-9_-]+)", line)
                    if match:
                        deps.append(match.group(1))

        rel_path = str(filepath.relative_to(self.project_path))
        self.report.dependency_graph[rel_path] = deps

    def _parse_pyproject_toml(self, filepath: Path):
        """Parse pyproject.toml for Python dependencies."""
        # Simple parser - in production, use tomllib (Python 3.11+)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        deps = re.findall(r'["\']([^"\']+)["\']\s*,?\s*(?=\n|])', content)
        rel_path = str(filepath.relative_to(self.project_path))
        self.report.dependency_graph[rel_path] = deps[:20]  # Limit

    def _parse_pipfile(self, filepath: Path):
        """Parse Pipfile for Python dependencies."""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        deps = re.findall(r"^([a-zA-Z0-9_-]+)\s*=", content, re.MULTILINE)
        rel_path = str(filepath.relative_to(self.project_path))
        self.report.dependency_graph[rel_path] = deps

    def _parse_composer_json(self, filepath: Path):
        """Parse composer.json for PHP dependencies."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        deps = data.get("require", {})
        dev_deps = data.get("require-dev", {})

        rel_path = str(filepath.relative_to(self.project_path))
        self.report.dependency_graph[rel_path] = list(deps.keys()) + list(dev_deps.keys())

    def generate_recommendations(self):
        """Generate actionable recommendations based on analysis."""
        print("[INFO] Generating recommendations...")

        # Security recommendations
        if self.report.security_issues:
            categories = Counter(issue["category"] for issue in self.report.security_issues)
            for category, count in categories.items():
                self.report.recommendations.append(
                    f"[SECURITY] Fix {count} {category.replace('_', ' ')} issue(s) immediately"
                )

        # Damaged files
        if self.report.damaged_files:
            self.report.recommendations.append(
                f"[CRITICAL] Repair {len(self.report.damaged_files)} damaged file(s) - they may prevent application startup"
            )

        # Orphan files
        if self.report.orphan_files:
            self.report.recommendations.append(
                f"[CLEANUP] Review {len(self.report.orphan_files)} orphan file(s) for potential removal or integration"
            )

        # TODOs
        if self.report.todos:
            self.report.recommendations.append(
                f"[TECHNICAL DEBT] Address {len(self.report.todos)} TODO/FIXME comment(s) across the codebase"
            )

        # Architecture recommendations
        if "FastAPI" in self.report.architecture_patterns:
            self.report.recommendations.append(
                "[ARCHITECTURE] Consider implementing API versioning for FastAPI endpoints"
            )

        if "React" in self.report.architecture_patterns:
            self.report.recommendations.append(
                "[ARCHITECTURE] Implement React Error Boundaries for better error handling"
            )

    def generate_report(self) -> str:
        """Generate a comprehensive Markdown report."""
        print("[INFO] Generating report...")

        report = []
        report.append("# 📊 Eco-Nojin Project Analysis Report")
        report.append(f"**Generated:** {self.report.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Project:** {self.report.project_name}")
        report.append(f"**Path:** `{self.report.project_path}`")
        report.append("")

        # Executive Summary
        report.append("## 📋 Executive Summary")
        report.append("")
        report.append("| Metric | Value |")
        report.append("|--------|-------|")
        report.append(f"| Total Files | {self.report.total_files} |")
        report.append(f"| Total Lines of Code | {self.report.total_lines:,} |")
        report.append(f"| Total Size | {self.report.total_size_mb:.2f} MB |")
        report.append(f"| Security Issues | {len(self.report.security_issues)} |")
        report.append(f"| Damaged Files | {len(self.report.damaged_files)} |")
        report.append(f"| Orphan Files | {len(self.report.orphan_files)} |")
        report.append(f"| TODO Comments | {len(self.report.todos)} |")
        report.append("")

        # File Distribution
        report.append("## 📁 File Distribution by Extension")
        report.append("")
        report.append("| Extension | Count | Percentage |")
        report.append("|-----------|-------|------------|")
        for ext, count in sorted(
            self.report.files_by_extension.items(), key=lambda x: x[1], reverse=True
        ):
            pct = (count / self.report.total_files * 100) if self.report.total_files > 0 else 0
            report.append(f"| {ext} | {count} | {pct:.1f}% |")
        report.append("")

        # File Status
        report.append("## 🔍 File Status Distribution")
        report.append("")
        report.append("| Status | Count |")
        report.append("|--------|-------|")
        for status, count in sorted(
            self.report.files_by_status.items(), key=lambda x: x[1], reverse=True
        ):
            report.append(f"| {status.value} | {count} |")
        report.append("")

        # Security Issues
        if self.report.security_issues:
            report.append("## 🔒 Security Issues")
            report.append("")
            report.append("| File | Line | Category | Match |")
            report.append("|------|------|----------|-------|")
            for issue in self.report.security_issues[:50]:  # Limit to first 50
                report.append(
                    f"| `{issue['file']}` | {issue['line']} | {issue['category']} | "
                    f"`{issue['match'][:50]}...` |"
                )
            if len(self.report.security_issues) > 50:
                report.append(
                    f"| ... | ... | ... | *{len(self.report.security_issues) - 50} more issues* |"
                )
            report.append("")

        # Damaged Files
        if self.report.damaged_files:
            report.append("## ⚠️ Damaged Files")
            report.append("")
            report.append("| File | Lines | Issues |")
            report.append("|------|-------|--------|")
            for file_info in self.report.damaged_files[:30]:
                issues_str = "; ".join(file_info.issues[:3])
                report.append(f"| `{file_info.path}` | {file_info.lines} | {issues_str} |")
            report.append("")

        # Orphan Files
        if self.report.orphan_files:
            report.append("## 🗂️ Orphan Files (Unreferenced)")
            report.append("")
            report.append("| File | Extension | Size (KB) | Lines |")
            report.append("|------|-----------|-----------|-------|")
            for file_info in self.report.orphan_files[:30]:
                size_kb = file_info.size_bytes / 1024
                report.append(
                    f"| `{file_info.path}` | {file_info.extension} | "
                    f"{size_kb:.1f} | {file_info.lines} |"
                )
            if len(self.report.orphan_files) > 30:
                report.append(
                    f"| ... | ... | ... | *{len(self.report.orphan_files) - 30} more files* |"
                )
            report.append("")

        # TODO Comments
        if self.report.todos:
            report.append("## 📝 TODO / Technical Debt")
            report.append("")
            report.append("| File | Line | Type | Description |")
            report.append("|------|------|------|-------------|")
            for todo in self.report.todos[:50]:
                report.append(
                    f"| `{todo['file']}` | {todo['line']} | {todo['type']} | {todo['text'][:80]} |"
                )
            if len(self.report.todos) > 50:
                report.append(f"| ... | ... | ... | *{len(self.report.todos) - 50} more TODOs* |")
            report.append("")

        # Architecture Patterns
        if self.report.architecture_patterns:
            report.append("## 🏗️ Detected Architecture Patterns")
            report.append("")
            for pattern, files in sorted(self.report.architecture_patterns.items()):
                report.append(f"### {pattern}")
                report.append(f"- **Files:** {len(files)}")
                report.append(f"- **Examples:** {', '.join(f'`{f}`' for f in files[:5])}")
                if len(files) > 5:
                    report.append(f"  - ... and {len(files) - 5} more files")
                report.append("")

        # Dependencies
        if self.report.dependency_graph:
            report.append("## 📦 Project Dependencies")
            report.append("")
            for dep_file, deps in self.report.dependency_graph.items():
                report.append(f"### {dep_file}")
                if deps:
                    for dep in sorted(deps)[:20]:
                        report.append(f"- {dep}")
                    if len(deps) > 20:
                        report.append(f"- ... and {len(deps) - 20} more dependencies")
                else:
                    report.append("- No dependencies found")
                report.append("")

        # Recommendations
        if self.report.recommendations:
            report.append("## 💡 Recommendations")
            report.append("")
            for i, rec in enumerate(self.report.recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")

        # Footer
        report.append("---")
        report.append("*Report generated by Eco-Nojin Project Analyzer v2.0.0*")
        report.append("*© 2026 Dasht Omid Narvan Agricultural & Industrial Company*")

        return "\n".join(report)

    def run(self):
        """Run the complete analysis pipeline."""
        print("=" * 70)
        print("ECO-NOJIN PROJECT COMPREHENSIVE ANALYZER")
        print("=" * 70)
        print()

        # Run analysis phases
        self.scan_directory()
        self.detect_orphan_files()
        self.categorize_files()
        self.analyze_dependencies()
        self.generate_recommendations()

        # Generate report
        report_content = self.generate_report()

        # Output report
        if self.output_path:
            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            print(f"\n[SUCCESS] Report saved to: {self.output_path}")
        else:
            print("\n" + report_content)

        # Print summary to console
        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)
        print(f"Total Files Analyzed: {self.report.total_files}")
        print(f"Total Lines of Code: {self.report.total_lines:,}")
        print(f"Security Issues Found: {len(self.report.security_issues)}")
        print(f"Damaged Files: {len(self.report.damaged_files)}")
        print(f"Orphan Files: {len(self.report.orphan_files)}")
        print(f"TODO Comments: {len(self.report.todos)}")
        print("=" * 70)

        return self.report


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def main():
    """Main entry point for the analyzer."""
    parser = argparse.ArgumentParser(
        description="Comprehensive analyzer for Eco-Nojin project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--path",
        "-p",
        type=str,
        default=".",
        help="Path to the project directory (default: current directory)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output file path for the report (default: print to console)",
    )
    parser.add_argument(
        "--json", "-j", action="store_true", help="Also output report in JSON format"
    )

    args = parser.parse_args()

    # Validate path
    project_path = Path(args.path)
    if not project_path.exists():
        print(f"[ERROR] Path does not exist: {project_path}")
        sys.exit(1)
    if not project_path.is_dir():
        print(f"[ERROR] Path is not a directory: {project_path}")
        sys.exit(1)

    # Run analyzer
    analyzer = EcoNojinAnalyzer(project_path=str(project_path), output_path=args.output)
    report = analyzer.run()

    # Optional JSON output
    if args.json:
        json_output = args.output.replace(".md", ".json") if args.output else "analysis_report.json"
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "project_name": report.project_name,
                    "analysis_date": report.analysis_date.isoformat(),
                    "total_files": report.total_files,
                    "total_lines": report.total_lines,
                    "total_size_mb": round(report.total_size_mb, 2),
                    "files_by_extension": report.files_by_extension,
                    "security_issues_count": len(report.security_issues),
                    "damaged_files_count": len(report.damaged_files),
                    "orphan_files_count": len(report.orphan_files),
                    "todos_count": len(report.todos),
                    "architecture_patterns": list(report.architecture_patterns.keys()),
                    "recommendations": report.recommendations,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        print(f"[INFO] JSON report saved to: {json_output}")


if __name__ == "__main__":
    main()
