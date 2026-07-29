#!/usr/bin/env python3
"""
Comparative Codebase Analyzer
Compares two directories based on software engineering quality metrics.
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

# --- Configuration & Exclusions ---
EXCLUDED_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.idea', '.vscode', 'dist', 'build', 'coverage'}
EXCLUDED_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.pdf', '.lock', '.pyc', '.pyo', '.tsbuildinfo'}

ADVANCED_MARKERS = [
    'pyproject.toml', 'docker-compose', 'Dockerfile', 'kubernetes', 'k8s', 
    'terraform', '.github/workflows', 'alembic', 'pytest.ini', 'ruff.toml',
    'hardhat.config', 'prometheus', 'grafana'
]

@dataclass
class CodebaseMetrics:
    path: str
    total_files: int = 0
    total_loc: int = 0  # Lines of Code (excluding blanks/comments)
    py_files: int = 0
    ts_files: int = 0
    test_files: int = 0
    advanced_markers_found: List[str] = field(default_factory=list)
    type_hint_score: float = 0.0  # Percentage of files with type hints
    docstring_score: float = 0.0  # Percentage of py files with docstrings

class CodebaseAnalyzer:
    def __init__(self, path_a: str, path_b: str):
        self.path_a = Path(path_a).resolve()
        self.path_b = Path(path_b).resolve()
        
        if not self.path_a.exists() or not self.path_b.exists():
            raise FileNotFoundError("One or both paths do not exist.")

    def _is_excluded(self, path: Path) -> bool:
        return any(part in EXCLUDED_DIRS for part in path.parts) or path.suffix in EXCLUDED_EXTS

    def _analyze_file(self, file_path: Path, metrics: CodebaseMetrics):
        metrics.total_files += 1
        ext = file_path.suffix.lower()
        
        if ext == '.py':
            metrics.py_files += 1
            if 'test' in file_path.name.lower() or file_path.parent.name == 'tests':
                metrics.test_files += 1
        elif ext in {'.ts', '.tsx', '.js', '.jsx'}:
            metrics.ts_files += 1
            if 'test' in file_path.name.lower() or 'spec' in file_path.name.lower():
                metrics.test_files += 1

        # Check for advanced markers in path or filename
        for marker in ADVANCED_MARKERS:
            if marker in str(file_path).lower():
                if marker not in metrics.advanced_markers_found:
                    metrics.advanced_markers_found.append(marker)

        # Quality Heuristics (Sample reading for performance)
        if ext in {'.py', '.ts', '.tsx'} and file_path.stat().st_size < 500_000: # Skip huge files
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    has_type_hint = False
                    has_docstring = False
                    
                    for i, line in enumerate(lines):
                        stripped = line.strip()
                        # Count real LOC
                        if stripped and not stripped.startswith(('#', '//', '/*', '*')):
                            metrics.total_loc += 1
                        
                        # Heuristic for Type Hints
                        if ext == '.py' and (re.search(r':\s*[A-Z]\w*', line) or re.search(r'->\s*[A-Z]\w*', line)):
                            has_type_hint = True
                        elif ext in {'.ts', '.tsx'} and (re.search(r':\s*[A-Z]\w*', line) or re.search(r'<[A-Z]\w*>', line)):
                            has_type_hint = True

                        # Heuristic for Docstrings
                        if ext == '.py' and (stripped.startswith('"""') or stripped.startswith("'''")):
                            has_docstring = True

                    if has_type_hint:
                        metrics.type_hint_score += 1
                    if has_docstring:
                        metrics.docstring_score += 1
                        
            except Exception:
                pass # Ignore unreadable files

    def analyze(self, target_path: Path) -> CodebaseMetrics:
        metrics = CodebaseMetrics(path=str(target_path))
        for root, dirs, files in os.walk(target_path):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for file in files:
                file_path = Path(root) / file
                if not self._is_excluded(file_path):
                    self._analyze_file(file_path, metrics)
        
        # Calculate percentages
        if metrics.py_files > 0:
            metrics.type_hint_score = (metrics.type_hint_score / metrics.py_files) * 100
            metrics.docstring_score = (metrics.docstring_score / metrics.py_files) * 100
        if metrics.ts_files > 0:
            # Approximate type hint score for TS based on overall TS files
            metrics.type_hint_score = max(metrics.type_hint_score, 85.0) # TS inherently has types
            
        return metrics

    def generate_report(self):
        print("\n" + "="*70)
        print("🔬 COMPARATIVE CODEBASE ANALYSIS REPORT")
        print("="*70)
        print(f"📍 Target A (Local):   {self.path_a}")
        print(f"📍 Target B (GitHub):  {self.path_b}\n")
        
        print("⏳ Analyzing Target A...")
        metrics_a = self.analyze(self.path_a)
        print("⏳ Analyzing Target B...")
        metrics_b = self.analyze(self.path_b)
        
        self._print_comparison(metrics_a, metrics_b)

    def _print_comparison(self, a: CodebaseMetrics, b: CodebaseMetrics):
        def colorize(val_a, val_b, is_higher_better=True):
            if val_a == val_b:
                return f"{val_a} (Equal)"
            winner_is_a = (val_a > val_b) if is_higher_better else (val_a < val_b)
            color = "\033[92m" if winner_is_a else "\033[91m" # Green if A wins, Red if B wins
            reset = "\033[0m"
            return f"{color}{val_a}{reset} vs {val_b}"

        print("-" * 70)
        print("📊 1. VOLUME & COVERAGE")
        print("-" * 70)
        print(f"Total Files (Excl. noise): {colorize(a.total_files, b.total_files)}")
        print(f"Real Lines of Code (LOC):  {colorize(a.total_loc, b.total_loc)}")
        print(f"Python Files:              {colorize(a.py_files, b.py_files)}")
        print(f"TypeScript/JS Files:       {colorize(a.ts_files, b.ts_files)}")
        print(f"Test Files:                {colorize(a.test_files, b.test_files)}")
        
        test_ratio_a = (a.test_files / a.total_files * 100) if a.total_files > 0 else 0
        test_ratio_b = (b.test_files / b.total_files * 100) if b.total_files > 0 else 0
        print(f"Test Coverage Ratio:       {colorize(f'{test_ratio_a:.1f}%', f'{test_ratio_b:.1f}%')}")

        print("\n" + "-" * 70)
        print("🏗️ 2. ARCHITECTURAL MATURITY")
        print("-" * 70)
        print(f"Advanced Markers Found:    {colorize(len(a.advanced_markers_found), len(b.advanced_markers_found))}")
        print(f"  -> Local (A):   {', '.join(a.advanced_markers_found[:5])}{'...' if len(a.advanced_markers_found)>5 else ''}")
        print(f"  -> GitHub (B):  {', '.join(b.advanced_markers_found[:5])}{'...' if len(b.advanced_markers_found)>5 else ''}")

        print("\n" + "-" * 70)
        print("✨ 3. CODE QUALITY HEURISTICS (Python/TS)")
        print("-" * 70)
        print(f"Type Hint Presence:        {colorize(f'{a.type_hint_score:.1f}%', f'{b.type_hint_score:.1f}%')}")
        print(f"Docstring Presence:        {colorize(f'{a.docstring_score:.1f}%', f'{b.docstring_score:.1f}%')}")

        print("\n" + "="*70)
        print("🏆 FINAL VERDICT")
        print("="*70)
        
        score_a = (a.total_loc * 0.2) + (a.test_files * 10) + (len(a.advanced_markers_found) * 50) + (a.type_hint_score * 2)
        score_b = (b.total_loc * 0.2) + (b.test_files * 10) + (len(b.advanced_markers_found) * 50) + (b.type_hint_score * 2)
        
        if score_a > score_b * 1.1:
            print("\033[92m✅ CONCLUSION: The LOCAL version (Drive D) is significantly more advanced.\033[0m")
            print("   Reason: Higher volume of meaningful code, more tests, or newer architectural markers.")
        elif score_b > score_a * 1.1:
            print("\033[91m⚠️ CONCLUSION: The GITHUB Repository is currently more advanced/complete.\033[0m")
            print("   Reason: The remote contains more structured code, tests, or mature configurations.")
        else:
            print("\033[93m⚖️ CONCLUSION: Both versions are roughly at parity, with minor local deviations.\033[0m")
            print("   Reason: Scores are within a 10% margin of each other.")
        print("="*70 + "\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        path1, path2 = sys.argv[1], sys.argv[2]
    else:
        # Default fallback based on user's environment
        path1 = r"D:\econojin.com"
        path2 = r"D:\github_reference\repo_github"
        print(f"Using default paths:\n A: {path1}\n B: {path2}\n")
        
    try:
        analyzer = CodebaseAnalyzer(path1, path2)
        analyzer.generate_report()
    except FileNotFoundError as e:
        print(f"\033[91m❌ Error: {e}\033[0m")
        print("Please ensure you have cloned the GitHub repo to the reference path first.")
    except Exception as e:
        print(f"\033[91m❌ Critical Error: {e}\033[0m")