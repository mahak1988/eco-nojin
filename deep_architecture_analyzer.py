#!/usr/bin/env python3
"""
Deep Architecture Analyzer (v1.1 - Patched)
Analyzes backend, frontend, and their connections for anti-patterns, 
security risks, and architectural mismatches.
"""

import ast
import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Set

# --- Configuration ---
TARGET_DIRS = ['apps', 'packages', 'src']
EXCLUDED_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build', 'migrations', 'tests', 'typechain-types'}
EXTENSIONS = {'.py', '.ts', '.tsx'}

# Severity Levels with ANSI Colors
SEVERITY = {
    'CRITICAL': '\033[91m[CRITICAL]\033[0m', 
    'HIGH': '\033[93m[HIGH]\033[0m', 
    'MEDIUM': '\033[94m[MEDIUM]\033[0m', 
    'LOW': '\033[96m[LOW]\033[0m'
}

@dataclass
class Finding:
    file: str
    line: int
    severity: str
    category: str
    message: str

class ArchitectureAnalyzer:
    def __init__(self, root_path: str):
        self.root = Path(root_path).resolve()
        self.findings: List[Finding] = []
        self.backend_routes: Set[str] = set()
        self.frontend_calls: Set[str] = set()

    def _is_excluded(self, path: Path) -> bool:
        return any(part in EXCLUDED_DIRS for part in path.parts)

    def run(self):
        print(f"🔬 Starting Deep Architecture Analysis on: {self.root}")
        print("-" * 70)
        
        for target in TARGET_DIRS:
            target_path = self.root / target
            if not target_path.exists():
                continue
                
            for root_dir, dirs, files in os.walk(target_path):
                # Modify dirs in-place to skip excluded directories efficiently
                dirs[:] = [d for d in dirs if not self._is_excluded(Path(root_dir) / d)]
                
                for file in files:
                    file_path = Path(root_dir) / file
                    if file_path.suffix in EXTENSIONS:
                        self._analyze_file(file_path)

        self._analyze_connections()
        self._generate_report()

    def _analyze_file(self, file_path: Path):
        rel_path = file_path.relative_to(self.root)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except (UnicodeDecodeError, PermissionError, OSError):
            return # Safely skip binary or unreadable files

        if file_path.suffix == '.py':
            self._analyze_python(rel_path, content, lines)
        elif file_path.suffix in {'.ts', '.tsx'}:
            self._analyze_typescript(rel_path, content, lines)

    def _analyze_python(self, rel_path: Path, content: str, lines: List[str]):
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            # 1. Check for missing return type hints in functions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name != '__init__' and node.returns is None:
                    self.findings.append(Finding(
                        file=str(rel_path), line=node.lineno, severity='MEDIUM',
                        category='Code Quality', message=f"Function '{node.name}' lacks a return type hint."
                    ))
                
                # 2. Check for blocking calls inside async functions
                if isinstance(node, ast.AsyncFunctionDef):
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Attribute) and child.func.attr in {'sleep'}:
                                self.findings.append(Finding(
                                    file=str(rel_path), line=child.lineno, severity='HIGH',
                                    category='Performance', message="Blocking call (e.g., time.sleep) detected inside async function."
                                ))

            # 3. Check for bare except clauses
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    self.findings.append(Finding(
                        file=str(rel_path), line=node.lineno, severity='CRITICAL',
                        category='Error Handling', message="Bare 'except:' clause detected. This catches SystemExit and KeyboardInterrupt."
                    ))

        # 4. Route Extraction (Simplified for analysis)
        route_matches = re.findall(r'@(?:app|router)\.(?:get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', content)
        for route in route_matches:
            self.backend_routes.add(route)

    def _analyze_typescript(self, rel_path: Path, content: str, lines: List[str]):
        # 1. Anti-pattern: fetch/axios inside useEffect
        useEffect_regex = re.compile(r'useEffect\s*\(\s*\(\)\s*=>\s*\{', re.MULTILINE)
        for match in useEffect_regex.finditer(content):
            start_pos = match.start()
            block = content[start_pos:start_pos+600] # Look ahead ~600 chars
            if 'fetch(' in block or 'axios.' in block or 'apiClient.' in block:
                line_no = content[:start_pos].count('\n') + 1
                self.findings.append(Finding(
                    file=str(rel_path), line=line_no, severity='HIGH',
                    category='State Management', message="Direct API call (fetch/axios) detected inside useEffect. Consider using React Query."
                ))

        # 2. Type Safety: Usage of 'any'
        any_regex = re.compile(r':\s*any\b')
        for match in any_regex.finditer(content):
            line_no = content[:match.start()].count('\n') + 1
            self.findings.append(Finding(
                file=str(rel_path), line=line_no, severity='MEDIUM',
                category='Type Safety', message="Usage of 'any' type detected. Define a proper interface or type."
            ))

        # 3. Hardcoded URLs (FIXED: using group(0) for the whole match)
        url_regex = re.compile(r'https?:\/\/(?:localhost|127\.0\.0\.1)[^"\'\s]+')
        for match in url_regex.finditer(content):
            line_no = content[:match.start()].count('\n') + 1
            self.findings.append(Finding(
                file=str(rel_path), line=line_no, severity='HIGH',
                category='Configuration', message=f"Hardcoded local URL detected: '{match.group(0)}'. Use environment variables."
            ))

        # 4. Frontend Call Extraction
        call_matches = re.findall(r'(?:get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', content)
        for call in call_matches:
            if not call.startswith('http'): # Relative paths only
                self.frontend_calls.add(call)

    def _analyze_connections(self):
        # Find frontend calls that have no matching backend route
        for call in self.frontend_calls:
            norm_call = call.rstrip('/')
            matched = False
            for route in self.backend_routes:
                norm_route = route.rstrip('/')
                if norm_call == norm_route or norm_call.startswith(norm_route + '/'):
                    matched = True
                    break
            
            if not matched:
                self.findings.append(Finding(
                    file="CONNECTION MISMATCH", line=0, severity='CRITICAL',
                    category='Integration', message=f"Frontend calls endpoint '{call}' but no matching route found in backend."
                ))

    def _generate_report(self):
        print("\n" + "="*70)
        print("📊 ARCHITECTURE ANALYSIS REPORT")
        print("="*70)
        
        if not self.findings:
            print("\n\033[92m✅ No major architectural anti-patterns detected.\033[0m\n")
            return

        findings_by_severity = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
        for f in self.findings:
            findings_by_severity[f.severity].append(f)

        total_issues = len(self.findings)
        print(f"\nTotal Issues Found: {total_issues}")
        print(f"  - Critical: {len(findings_by_severity['CRITICAL'])}")
        print(f"  - High: {len(findings_by_severity['HIGH'])}")
        print(f"  - Medium: {len(findings_by_severity['MEDIUM'])}\n")
        print("-" * 70)

        for severity in ['CRITICAL', 'HIGH', 'MEDIUM']:
            if findings_by_severity[severity]:
                print(f"\n{SEVERITY[severity]} {severity} ISSUES:")
                for f in findings_by_severity[severity][:20]: # Limit output to prevent console spam
                    print(f"  • {f.file}:{f.line} | {f.category}")
                    print(f"    {f.message}")
                if len(findings_by_severity[severity]) > 20:
                    print(f"  ... and {len(findings_by_severity[severity]) - 20} more {severity.lower()} issues.")

        print("\n" + "="*70)
        print("💡 RECOMMENDATION: Address all CRITICAL and HIGH issues before")
        print("   proceeding with new feature development to ensure system stability.")
        print("="*70 + "\n")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    try:
        analyzer = ArchitectureAnalyzer(target_dir)
        analyzer.run()
    except Exception as e:
        print(f"\n\033[91m❌ Critical Error during analysis: {e}\033[0m")
        sys.exit(1)