#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Comprehensive Project Analyzer v3.0
===============================================
اسکریپت جامع آنالیز معماری، کیفیت و سلامت پروژه

ویژگی‌ها:
- آنالیز ۹ لایه‌ای (ساختار، وابستگی، کیفیت، معماری، امنیت، ...)
- استفاده از AST برای دقت بالا در Python
- محاسبه معیارهای Robert C. Martin (Coupling, Cohesion, Instability)
- شناسایی الگوهای DDD و Clean Architecture
- تشخیص بدهی فنی و مشکلات امنیتی
- خروجی چندگانه: JSON, Terminal (رنگی), HTML

نویسنده: Eco Nojin Architecture Team
نسخه: 3.0.0
تاریخ: 2026-07-12

نحوه اجرا:
    python scripts/analyze_project.py
    python scripts/analyze_project.py --output html
    python scripts/analyze_project.py --modules ai_agents,simulation
"""

import ast
import json
import os
import re
import sys
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import hashlib
import argparse

# ============================================================
# تنظیمات و ثابت‌ها
# ============================================================

VERSION = "3.0.0"
PROJECT_NAME = "Eco Nojin"

# دایرکتوری‌ها و فایل‌های مستثنی
EXCLUDED_DIRS = {
    "__pycache__", "node_modules", ".venv", "venv", "env",
    ".git", ".idea", ".vscode", "dist", "build", ".next",
    ".turbo", "coverage", ".pytest_cache", ".mypy_cache",
    "migrations", "alembic", ".cache", ".pnpm-store"
}

EXCLUDED_FILE_PATTERNS = [
    r".*\.min\.js$", r".*\.min\.css$", r".*\.lock$",
    r".*\.map$", r".*\.pyc$", r"package-lock\.json$",
    r"pnpm-lock\.yaml$", r"yarn\.lock$"
]

PYTHON_EXTENSIONS = {".py", ".pyi"}
TYPESCRIPT_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml"}

# الگوهای معماری (Pattern Detection)
ARCHITECTURE_PATTERNS = {
    "router": re.compile(r"(APIRouter|FastAPI|router\s*=|@app\.(get|post|put|delete))", re.IGNORECASE),
    "repository": re.compile(r"(class\s+\w+Repository|BaseRepository|async\s+def\s+(get_all|get_by_id|create|update|delete))", re.IGNORECASE),
    "service": re.compile(r"(class\s+\w+Service|def\s+\w+_service)", re.IGNORECASE),
    "model": re.compile(r"(class\s+\w+\(Base\)|BaseModel|Column\(|relationship\()", re.IGNORECASE),
    "schema": re.compile(r"(class\s+\w+(Schema|Request|Response|DTO)\(BaseModel\))", re.IGNORECASE),
    "usecase": re.compile(r"(class\s+\w+(UseCase|Interactor)|def\s+execute)", re.IGNORECASE),
    "agent": re.compile(r"(class\s+\w+Agent|BaseAgent|StructuredChatAgent)", re.IGNORECASE),
    "tool": re.compile(r"(@tool|BaseTool|Tool\s*=)", re.IGNORECASE),
    "orchestrator": re.compile(r"(class\s+\w+Orchestrator|StateGraph|CompiledGraph)", re.IGNORECASE),
    "controller": re.compile(r"(class\s+\w+Controller|@controller)", re.IGNORECASE),
}

# نشانگرهای بدهی فنی
DEBT_MARKERS = {
    "TODO": re.compile(r"#\s*TODO[:\s](.+)", re.IGNORECASE),
    "FIXME": re.compile(r"#\s*FIXME[:\s](.+)", re.IGNORECASE),
    "HACK": re.compile(r"#\s*HACK[:\s](.+)", re.IGNORECASE),
    "XXX": re.compile(r"#\s*XXX[:\s](.+)", re.IGNORECASE),
    "BUG": re.compile(r"#\s*BUG[:\s](.+)", re.IGNORECASE),
}

# الگوهای امنیتی
SECURITY_PATTERNS = {
    "hardcoded_secret": re.compile(
        r"(?i)(password|secret|api_key|apikey|token|private_key)\s*=\s*['\"][^'\"]{8,}['\"]"
    ),
    "debug_true": re.compile(r"DEBUG\s*=\s*True"),
    "cors_wildcard": re.compile(r'allow_origins\s*=\s*\[\s*["\']\*["\']\s*\]'),
    "sql_injection": re.compile(r"execute\s*\(\s*f['\"]|execute\s*\(\s*['\"].*%s"),
    "eval_usage": re.compile(r"\beval\s*\("),
    "exec_usage": re.compile(r"\bexec\s*\("),
    "pickle_load": re.compile(r"pickle\.load\s*\("),
    "yaml_unsafe": re.compile(r"yaml\.load\s*\((?!.*Loader)"),
}

# ============================================================
# Data Models
# ============================================================

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class FileMetrics:
    """معیارهای یک فایل"""
    path: str
    language: str
    size_bytes: int = 0
    lines_total: int = 0
    lines_code: int = 0
    lines_comment: int = 0
    lines_blank: int = 0
    functions: int = 0
    classes: int = 0
    imports: int = 0
    complexity: float = 0.0  # Cyclomatic complexity
    docstring_ratio: float = 0.0
    last_modified: str = ""

@dataclass
class ModuleMetrics:
    """معیارهای یک ماژول"""
    name: str
    path: str
    total_files: int = 0
    total_lines: int = 0
    languages: Dict[str, int] = field(default_factory=dict)
    patterns: Dict[str, int] = field(default_factory=dict)
    avg_complexity: float = 0.0
    max_complexity: float = 0.0
    docstring_coverage: float = 0.0
    test_ratio: float = 0.0
    debt_markers: Dict[str, int] = field(default_factory=dict)
    security_issues: List[Dict] = field(default_factory=list)
    internal_deps: int = 0
    external_deps: int = 0
    afferent_coupling: int = 0  # Ca
    efferent_coupling: int = 0  # Ce
    instability: float = 0.0
    abstractness: float = 0.0
    distance_from_main: float = 0.0

@dataclass
class DependencyEdge:
    """یک یال در گراف وابستگی"""
    source: str
    target: str
    imports: List[str] = field(default_factory=list)
    count: int = 1

@dataclass
class Finding:
    """یک یافته (مشکل یا توصیه)"""
    id: str
    category: str
    severity: str
    message: str
    file: str = ""
    line: int = 0
    recommendation: str = ""

@dataclass
class AnalysisReport:
    """گزارش نهایی تحلیل"""
    timestamp: str
    project_name: str
    project_root: str
    version: str
    summary: Dict[str, Any]
    modules: Dict[str, ModuleMetrics]
    dependencies: List[Dict]
    findings: List[Finding]
    recommendations: List[Dict]

# ============================================================
# Terminal Colors
# ============================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

def cprint(msg: str, color: str = Colors.END, end: str = "\n"):
    """چاپ رنگی"""
    print(f"{color}{msg}{Colors.END}", end=end)

# ============================================================
# Python AST Analyzer
# ============================================================

class PythonAnalyzer:
    """تحلیلگر فایل‌های Python با استفاده از AST"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = ""
        self.tree = None
        self.metrics = FileMetrics(
            path=str(file_path),
            language="python"
        )
    
    def analyze(self) -> Optional[FileMetrics]:
        """انجام تحلیل کامل"""
        try:
            self.content = self.file_path.read_text(encoding="utf-8")
            self.metrics.size_bytes = len(self.content.encode("utf-8"))
            self._count_lines()
            self._parse_ast()
            self._analyze_ast()
            self.metrics.last_modified = datetime.fromtimestamp(
                self.file_path.stat().st_mtime
            ).isoformat()
            return self.metrics
        except Exception as e:
            print(f"{Colors.DIM}  ⚠️  خطا در تحلیل {self.file_path}: {e}{Colors.END}")
            return None
    
    def _count_lines(self):
        """شمارش خطوط"""
        lines = self.content.split("\n")
        self.metrics.lines_total = len(lines)
        self.metrics.lines_blank = sum(1 for l in lines if not l.strip())
        
        # شمارش کامنت‌ها (تقریبی)
        in_docstring = False
        docstring_char = None
        comment_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not in_docstring:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    docstring_char = stripped[:3]
                    in_docstring = True
                    if stripped.count(docstring_char) >= 2:
                        in_docstring = False
                    comment_lines += 1
                elif stripped.startswith("#"):
                    comment_lines += 1
            else:
                comment_lines += 1
                if docstring_char in stripped:
                    in_docstring = False
        
        self.metrics.lines_comment = comment_lines
        self.metrics.lines_code = self.metrics.lines_total - comment_lines - self.metrics.lines_blank
    
    def _parse_ast(self):
        """پارس کردن AST"""
        try:
            self.tree = ast.parse(self.content, filename=str(self.file_path))
        except SyntaxError:
            self.tree = None
    
    def _analyze_ast(self):
        """تحلیل AST برای استخراج معیارها"""
        if not self.tree:
            return
        
        functions = 0
        classes = 0
        imports = 0
        total_funcs_with_doc = 0
        total_funcs = 0
        complexity_sum = 0
        
        for node in ast.walk(self.tree):
            # شمارش توابع
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions += 1
                total_funcs += 1
                if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)):
                    total_funcs_with_doc += 1
                
                # محاسبه پیچیدگی cyclomatic
                complexity_sum += self._calculate_complexity(node)
            
            # شمارش کلاس‌ها
            elif isinstance(node, ast.ClassDef):
                classes += 1
            
            # شمارش importها
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports += 1
        
        self.metrics.functions = functions
        self.metrics.classes = classes
        self.metrics.imports = imports
        self.metrics.complexity = (complexity_sum / functions) if functions > 0 else 0
        self.metrics.docstring_ratio = (total_funcs_with_doc / total_funcs) if total_funcs > 0 else 0
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """محاسبه Cyclomatic Complexity برای یک تابع"""
        complexity = 1  # مسیر پایه
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += 1
            elif isinstance(child, ast.Assert):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
                complexity += len(child.ifs)
        
        return complexity
    
    def extract_imports(self) -> List[Tuple[str, str]]:
        """استخراج لیست importها به صورت (module, source_type)"""
        if not self.tree:
            return []
        
        imports = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((alias.name, "absolute"))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append((node.module, "from"))
        
        return imports
    
    def extract_docstrings(self) -> List[str]:
        """استخراج docstringهای ماژول و کلاس‌ها"""
        if not self.tree:
            return []
        
        docstrings = []
        
        # Module docstring
        if (self.tree.body and isinstance(self.tree.body[0], ast.Expr) and
            isinstance(self.tree.body[0].value, ast.Constant) and
            isinstance(self.tree.body[0].value.value, str)):
            docstrings.append(self.tree.body[0].value.value)
        
        # Class and Function docstrings
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)):
                    docstrings.append(node.body[0].value.value)
        
        return docstrings

# ============================================================
# TypeScript Analyzer (Regex-based)
# ============================================================

class TypeScriptAnalyzer:
    """تحلیلگر فایل‌های TypeScript/JavaScript"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = ""
        self.metrics = FileMetrics(
            path=str(file_path),
            language=file_path.suffix[1:]  # ts, tsx, js, jsx
        )
    
    def analyze(self) -> Optional[FileMetrics]:
        try:
            self.content = self.file_path.read_text(encoding="utf-8")
            self.metrics.size_bytes = len(self.content.encode("utf-8"))
            self._count_lines()
            self._analyze_patterns()
            self.metrics.last_modified = datetime.fromtimestamp(
                self.file_path.stat().st_mtime
            ).isoformat()
            return self.metrics
        except Exception as e:
            return None
    
    def _count_lines(self):
        lines = self.content.split("\n")
        self.metrics.lines_total = len(lines)
        self.metrics.lines_blank = sum(1 for l in lines if not l.strip())
        
        # شمارش کامنت‌ها
        comment_lines = 0
        in_block_comment = False
        for line in lines:
            stripped = line.strip()
            if in_block_comment:
                comment_lines += 1
                if "*/" in stripped:
                    in_block_comment = False
            elif stripped.startswith("//"):
                comment_lines += 1
            elif stripped.startswith("/*"):
                comment_lines += 1
                if "*/" not in stripped:
                    in_block_comment = True
        
        self.metrics.lines_comment = comment_lines
        self.metrics.lines_code = self.metrics.lines_total - comment_lines - self.metrics.lines_blank
    
    def _analyze_patterns(self):
        # شمارش توابع
        self.metrics.functions = len(re.findall(
            r"(?:function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?(?:\([^)]*\)|[^=])\s*=>)",
            self.content
        ))
        
        # شمارش کلاس‌ها
        self.metrics.classes = len(re.findall(r"\bclass\s+\w+", self.content))
        
        # شمارش importها
        self.metrics.imports = len(re.findall(r"\bimport\s+.*\bfrom\b|\bimport\s+['\"]", self.content))
        
        # پیچیدگی تقریبی
        conditionals = len(re.findall(r"\b(if|else|while|for|switch|case|\?|&&|\|\|)\b", self.content))
        self.metrics.complexity = 1 + (conditionals / max(1, self.metrics.functions))

# ============================================================
# Project Analyzer (Orchestrator)
# ============================================================

class ProjectAnalyzer:
    """تحلیلگر اصلی پروژه"""
    
    def __init__(self, project_root: Path, target_modules: Optional[List[str]] = None):
        self.project_root = project_root
        self.apps_dir = project_root / "apps"
        self.target_modules = target_modules
        self.file_metrics: Dict[str, FileMetrics] = {}
        self.module_metrics: Dict[str, ModuleMetrics] = {}
        self.dependencies: List[DependencyEdge] = []
        self.findings: List[Finding] = []
        self.import_graph: Dict[str, Set[str]] = defaultdict(set)  # module -> set of modules it imports
    
    def analyze(self) -> AnalysisReport:
        """اجرای تحلیل کامل"""
        cprint("\n" + "=" * 70, Colors.HEADER)
        cprint(f"🔬 {PROJECT_NAME} - Comprehensive Project Analyzer v{VERSION}", Colors.HEADER)
        cprint("=" * 70, Colors.HEADER)
        
        # ۱. اسکن فایل‌ها
        cprint("\n📂 مرحله ۱: اسکن ساختار فایل‌ها...", Colors.BLUE)
        all_files = self._scan_files()
        cprint(f"   ✅ {len(all_files)} فایل شناسایی شد", Colors.GREEN)
        
        # ۲. تحلیل فایل‌ها
        cprint("\n🔍 مرحله ۲: تحلیل محتوای فایل‌ها...", Colors.BLUE)
        self._analyze_files(all_files)
        cprint(f"   ✅ {len(self.file_metrics)} فایل تحلیل شد", Colors.GREEN)
        
        # ۳. محاسبه معیارهای ماژول
        cprint("\n📊 مرحله ۳: محاسبه معیارهای ماژول‌ها...", Colors.BLUE)
        self._compute_module_metrics()
        cprint(f"   ✅ {len(self.module_metrics)} ماژول محاسبه شد", Colors.GREEN)
        
        # ۴. تحلیل گراف وابستگی
        cprint("\n🕸️  مرحله ۴: تحلیل گراف وابستگی...", Colors.BLUE)
        self._analyze_dependencies()
        cprint(f"   ✅ {len(self.dependencies)} یال وابستگی شناسایی شد", Colors.GREEN)
        
        # ۵. محاسبه معیارهای معماری (Robert C. Martin)
        cprint("\n🏛️  مرحله ۵: محاسبه معیارهای معماری...", Colors.BLUE)
        self._compute_architecture_metrics()
        
        # ۶. شناسایی مشکلات و توصیه‌ها
        cprint("\n⚠️  مرحله ۶: شناسایی مشکلات و توصیه‌ها...", Colors.BLUE)
        self._identify_findings()
        cprint(f"   ✅ {len(self.findings)} یافته شناسایی شد", Colors.GREEN)
        
        # ۷. تولید گزارش
        cprint("\n📝 مرحله ۷: تولید گزارش نهایی...", Colors.BLUE)
        report = self._generate_report()
        
        return report
    
    def _scan_files(self) -> List[Path]:
        """اسکن تمام فایل‌های پروژه"""
        files = []
        
        if not self.apps_dir.exists():
            cprint(f"   ❌ پوشه apps یافت نشد: {self.apps_dir}", Colors.RED)
            return files
        
        for path in self.apps_dir.rglob("*"):
            if not path.is_file():
                continue
            
            # بررسی استثناها
            if any(part in EXCLUDED_DIRS for part in path.parts):
                continue
            
            if any(re.match(p, path.name) for p in EXCLUDED_FILE_PATTERNS):
                continue
            
            # بررسی ماژول‌های هدف
            if self.target_modules:
                rel = path.relative_to(self.apps_dir)
                if rel.parts[0] not in self.target_modules:
                    continue
            
            files.append(path)
        
        return files
    
    def _analyze_files(self, files: List[Path]):
        """تحلیل محتوای فایل‌ها"""
        for i, file_path in enumerate(files, 1):
            if i % 50 == 0:
                cprint(f"   ⏳ تحلیل {i}/{len(files)}...", Colors.DIM)
            
            ext = file_path.suffix
            metrics = None
            
            if ext in PYTHON_EXTENSIONS:
                analyzer = PythonAnalyzer(file_path)
                metrics = analyzer.analyze()
            elif ext in TYPESCRIPT_EXTENSIONS:
                analyzer = TypeScriptAnalyzer(file_path)
                metrics = analyzer.analyze()
            elif ext in CONFIG_EXTENSIONS:
                metrics = FileMetrics(
                    path=str(file_path),
                    language=ext[1:],
                    size_bytes=file_path.stat().st_size
                )
            else:
                metrics = FileMetrics(
                    path=str(file_path),
                    language="other",
                    size_bytes=file_path.stat().st_size
                )
            
            if metrics:
                self.file_metrics[str(file_path)] = metrics
    
    def _compute_module_metrics(self):
        """محاسبه معیارهای هر ماژول"""
        # گروه‌بندی فایل‌ها بر اساس ماژول
        module_files: Dict[str, List[FileMetrics]] = defaultdict(list)
        
        for file_path_str, metrics in self.file_metrics.items():
            file_path = Path(file_path_str)
            try:
                rel = file_path.relative_to(self.apps_dir)
                module_name = rel.parts[0]
                module_files[module_name].append(metrics)
            except ValueError:
                continue
        
        # محاسبه معیارها برای هر ماژول
        for module_name, files in module_files.items():
            module_path = self.apps_dir / module_name
            module_metrics = ModuleMetrics(
                name=module_name,
                path=str(module_path),
                total_files=len(files)
            )
            
            # آمار زبان‌ها
            lang_counter = Counter(f.language for f in files)
            module_metrics.languages = dict(lang_counter)
            
            # مجموع خطوط
            module_metrics.total_lines = sum(f.lines_total for f in files)
            
            # پیچیدگی
            complexities = [f.complexity for f in files if f.complexity > 0]
            if complexities:
                module_metrics.avg_complexity = sum(complexities) / len(complexities)
                module_metrics.max_complexity = max(complexities)
            
            # پوشش docstring
            doc_ratios = [f.docstring_ratio for f in files if f.language == "python" and f.functions > 0]
            if doc_ratios:
                module_metrics.docstring_coverage = sum(doc_ratios) / len(doc_ratios)
            
            # نسبت تست
            test_files = [f for f in files if "test" in Path(f.path).name.lower()]
            non_test_files = [f for f in files if "test" not in Path(f.path).name.lower()]
            if non_test_files:
                module_metrics.test_ratio = len(test_files) / (len(test_files) + len(non_test_files))
            
            # شناسایی الگوهای معماری
            self._detect_patterns(module_name, files, module_metrics)
            
            # شناسایی بدهی فنی و مشکلات امنیتی
            self._scan_debt_and_security(module_name, files, module_metrics)
            
            self.module_metrics[module_name] = module_metrics
    
    def _detect_patterns(self, module_name: str, files: List[FileMetrics], 
                         module_metrics: ModuleMetrics):
        """شناسایی الگوهای معماری در ماژول"""
        pattern_counts = defaultdict(int)
        
        for file_metrics in files:
            if not file_metrics.path.endswith(".py"):
                continue
            
            try:
                content = Path(file_metrics.path).read_text(encoding="utf-8")
                for pattern_name, pattern_regex in ARCHITECTURE_PATTERNS.items():
                    if pattern_regex.search(content):
                        pattern_counts[pattern_name] += 1
            except Exception:
                continue
        
        module_metrics.patterns = dict(pattern_counts)
    
    def _scan_debt_and_security(self, module_name: str, files: List[FileMetrics],
                                 module_metrics: ModuleMetrics):
        """اسکن بدهی فنی و مشکلات امنیتی"""
        debt_counts = defaultdict(int)
        security_issues = []
        
        for file_metrics in files:
            if file_metrics.language not in ["py", "ts", "tsx", "js", "jsx"]:
                continue
            
            try:
                content = Path(file_metrics.path).read_text(encoding="utf-8")
                lines = content.split("\n")
                
                # بدهی فنی
                for i, line in enumerate(lines, 1):
                    for marker, pattern in DEBT_MARKERS.items():
                        match = pattern.search(line)
                        if match:
                            debt_counts[marker] += 1
                            if marker in ["FIXME", "BUG"]:
                                security_issues.append({
                                    "type": "debt_marker",
                                    "severity": Severity.MEDIUM.value,
                                    "file": file_metrics.path,
                                    "line": i,
                                    "message": f"{marker}: {match.group(1).strip()[:80]}"
                                })
                
                # مشکلات امنیتی
                for pattern_name, pattern_regex in SECURITY_PATTERNS.items():
                    for i, line in enumerate(lines, 1):
                        if pattern_regex.search(line):
                            severity = Severity.HIGH.value if pattern_name in [
                                "hardcoded_secret", "eval_usage", "exec_usage"
                            ] else Severity.MEDIUM.value
                            security_issues.append({
                                "type": pattern_name,
                                "severity": severity,
                                "file": file_metrics.path,
                                "line": i,
                                "message": f"الگوی ناامن: {pattern_name}"
                            })
            except Exception:
                continue
        
        module_metrics.debt_markers = dict(debt_counts)
        module_metrics.security_issues = security_issues
    
    def _analyze_dependencies(self):
        """تحلیل گراف وابستگی بین ماژول‌ها"""
        # فقط برای فایل‌های Python
        for file_path_str, metrics in self.file_metrics.items():
            if not file_path_str.endswith(".py"):
                continue
            
            file_path = Path(file_path_str)
            try:
                rel = file_path.relative_to(self.apps_dir)
                source_module = rel.parts[0]
            except ValueError:
                continue
            
            analyzer = PythonAnalyzer(file_path)
            analyzer.content = file_path.read_text(encoding="utf-8")
            analyzer._parse_ast()
            imports = analyzer.extract_imports()
            
            for module_name, _ in imports:
                # تشخیص ماژول‌های داخلی (apps.*)
                if module_name.startswith("apps."):
                    parts = module_name.split(".")
                    if len(parts) >= 2:
                        target_module = parts[1]
                        if target_module != source_module:
                            self.import_graph[source_module].add(target_module)
                            self.dependencies.append(DependencyEdge(
                                source=source_module,
                                target=target_module,
                                imports=[module_name]
                            ))
    
    def _compute_architecture_metrics(self):
        """محاسبه معیارهای Robert C. Martin"""
        # محاسبه Ca (Afferent Coupling) و Ce (Efferent Coupling)
        afferent = defaultdict(int)  # چه ماژول‌هایی به این ماژول وابسته‌اند
        efferent = defaultdict(int)  # این ماژول به چه ماژول‌هایی وابسته است
        
        for source, targets in self.import_graph.items():
            efferent[source] = len(targets)
            for target in targets:
                afferent[target] += 1
        
        for module_name, metrics in self.module_metrics.items():
            ca = afferent.get(module_name, 0)
            ce = efferent.get(module_name, 0)
            
            metrics.afferent_coupling = ca
            metrics.efferent_coupling = ce
            
            # Instability: I = Ce / (Ca + Ce)
            if ca + ce > 0:
                metrics.instability = ce / (ca + ce)
            else:
                metrics.instability = 0.5
            
            # Abstractness: نسبت کلاس‌های abstract به کل
            # تخمین: ماژول‌هایی با patterns شامل interface/schema abstractness بالاتری دارند
            abstract_patterns = metrics.patterns.get("schema", 0) + metrics.patterns.get("model", 0)
            total_patterns = sum(metrics.patterns.values()) or 1
            metrics.abstractness = abstract_patterns / total_patterns
            
            # Distance from Main Sequence: D = |A + I - 1|
            metrics.distance_from_main = abs(metrics.abstractness + metrics.instability - 1)
    
    def _identify_findings(self):
        """شناسایی مشکلات و تولید توصیه‌ها"""
        finding_id = 0
        
        for module_name, metrics in self.module_metrics.items():
            # ۱. بررسی Fat Module
            if metrics.total_files > 50:
                finding_id += 1
                self.findings.append(Finding(
                    id=f"F-{finding_id:03d}",
                    category="Architecture",
                    severity=Severity.HIGH.value,
                    message=f"ماژول '{module_name}' بسیار بزرگ است ({metrics.total_files} فایل)",
                    recommendation="ماژول را به زیرماژول‌های کوچکتر تقسیم کنید"
                ))
            
            # ۲. بررسی پیچیدگی بالا
            if metrics.max_complexity > 15:
                finding_id += 1
                self.findings.append(Finding(
                    id=f"F-{finding_id:03d}",
                    category="Quality",
                    severity=Severity.HIGH.value,
                    message=f"پیچیدگی بسیار بالا در '{module_name}' (max: {metrics.max_complexity:.1f})",
                    recommendation="توابع پیچیده را به توابع کوچکتر تقسیم کنید"
                ))
            
            # ۳. بررسی پوشش تست پایین
            if metrics.test_ratio < 0.1 and metrics.total_files > 5:
                finding_id += 1
                self.findings.append(Finding(
                    id=f"F-{finding_id:03d}",
                    category="Testing",
                    severity=Severity.MEDIUM.value,
                    message=f"پوشش تست بسیار پایین در '{module_name}' ({metrics.test_ratio*100:.1f}%)",
                    recommendation="تست‌های واحد برای توابع حیاتی بنویسید"
                ))
            
            # ۴. بررسی Instability بالا
            if metrics.instability > 0.8 and metrics.afferent_coupling > 2:
                finding_id += 1
                self.findings.append(Finding(
                    id=f"F-{finding_id:03d}",
                    category="Architecture",
                    severity=Severity.HIGH.value,
                    message=f"ماژول '{module_name}' ناپایدار است (I={metrics.instability:.2f}, Ca={metrics.afferent_coupling})",
                    recommendation="ماژول‌های وابسته به این ماژول زیادند اما خود ناپایدار است. API را پایدار کنید."
                ))
            
            # ۵. بررسی مشکلات امنیتی
            critical_security = [i for i in metrics.security_issues 
                                if i["severity"] == Severity.HIGH.value]
            if critical_security:
                finding_id += 1
                self.findings.append(Finding(
                    id=f"F-{finding_id:03d}",
                    category="Security",
                    severity=Severity.CRITICAL.value,
                    message=f"{len(critical_security)} مشکل امنیتی بحرانی در '{module_name}'",
                    recommendation="مشکلات امنیتی را فوراً رفع کنید"
                ))
            
            # ۶. بررسی بدهی فنی بالا
            total_debt = sum(metrics.debt_markers.values())
            if total_debt > 20:
                finding_id += 1
                self.findings.append(Finding(
                    id=f"F-{finding_id:03d}",
                    category="Debt",
                    severity=Severity.MEDIUM.value,
                    message=f"بدهی فنی بالا در '{module_name}' ({total_debt} نشانگر)",
                    recommendation="بدهی فنی را در اسپرینت‌های آتی رفع کنید"
                ))
            
            # ۷. بررسی پوشش docstring
            if metrics.docstring_coverage < 0.3 and metrics.languages.get("py", 0) > 5:
                finding_id += 1
                self.findings.append(Finding(
                    id=f"F-{finding_id:03d}",
                    category="Documentation",
                    severity=Severity.LOW.value,
                    message=f"پوشش مستندات پایین در '{module_name}' ({metrics.docstring_coverage*100:.1f}%)",
                    recommendation="برای توابع عمومی docstring بنویسید"
                ))
        
        # ۸. بررسی وابستگی‌های دایره‌ای
        cycles = self._detect_cycles()
        if cycles:
            finding_id += 1
            self.findings.append(Finding(
                id=f"F-{finding_id:03d}",
                category="Architecture",
                severity=Severity.CRITICAL.value,
                message=f"وابستگی دایره‌ای بین ماژول‌ها شناسایی شد: {cycles}",
                recommendation="وابستگی‌های دایره‌ای را با استفاده از Dependency Inversion رفع کنید"
            ))
    
    def _detect_cycles(self) -> List[List[str]]:
        """شناسایی چرخه‌ها در گراف وابستگی (DFS)"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.import_graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    # چرخه پیدا شد
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            path.pop()
            rec_stack.remove(node)
        
        for module in self.import_graph.keys():
            if module not in visited:
                dfs(module, [])
        
        return cycles
    
    def _generate_report(self) -> AnalysisReport:
        """تولید گزارش نهایی"""
        # محاسبه آمار کلی
        total_files = len(self.file_metrics)
        total_lines = sum(m.lines_total for m in self.file_metrics.values())
        total_functions = sum(m.functions for m in self.file_metrics.values())
        total_classes = sum(m.classes for m in self.file_metrics.values())
        
        # توزیع زبان‌ها
        lang_counter = Counter(m.language for m in self.file_metrics.values())
        
        # میانگین پیچیدگی کل
        complexities = [m.complexity for m in self.file_metrics.values() if m.complexity > 0]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        
        summary = {
            "total_files": total_files,
            "total_lines": total_lines,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "total_modules": len(self.module_metrics),
            "languages": dict(lang_counter),
            "avg_complexity": round(avg_complexity, 2),
            "total_findings": len(self.findings),
            "critical_findings": len([f for f in self.findings if f.severity == Severity.CRITICAL.value]),
            "high_findings": len([f for f in self.findings if f.severity == Severity.HIGH.value]),
        }
        
        # تولید توصیه‌ها
        recommendations = self._generate_recommendations()
        
        return AnalysisReport(
            timestamp=datetime.now().isoformat(),
            project_name=PROJECT_NAME,
            project_root=str(self.project_root),
            version=VERSION,
            summary=summary,
            modules={k: asdict(v) for k, v in self.module_metrics.items()},
            dependencies=[asdict(d) for d in self.dependencies],
            findings=self.findings,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self) -> List[Dict]:
        """تولید توصیه‌های استراتژیک"""
        recommendations = []
        
        # تحلیل ماژول shared
        if "shared" in self.module_metrics:
            shared = self.module_metrics["shared"]
            if shared.total_files > 30:
                recommendations.append({
                    "priority": "high",
                    "category": "Architecture",
                    "message": "ماژول shared بسیار بزرگ است. به shared-core, shared-ai, shared-sim تقسیم کنید."
                })
        
        # تحلیل وابستگی‌ها
        if self.import_graph:
            most_depended = max(self.import_graph.items(), key=lambda x: len(x[1]))
            if len(most_depended[1]) > 5:
                recommendations.append({
                    "priority": "medium",
                    "category": "Architecture",
                    "message": f"ماژول '{most_depended[0]}' به {len(most_depended[1])} ماژول دیگر وابسته است. وابستگی را کاهش دهید."
                })
        
        # تحلیل کیفیت کلی
        all_complexities = [m.avg_complexity for m in self.module_metrics.values() if m.avg_complexity > 0]
        if all_complexities:
            avg = sum(all_complexities) / len(all_complexities)
            if avg > 10:
                recommendations.append({
                    "priority": "high",
                    "category": "Quality",
                    "message": f"میانگین پیچیدگی کل پروژه ({avg:.1f}) بالاست. بازبینی کد لازم است."
                })
        
        return recommendations
    
    def print_summary(self, report: AnalysisReport):
        """چاپ خلاصه گزارش در ترمینال"""
        cprint("\n" + "=" * 70, Colors.HEADER)
        cprint("📊 خلاصه تحلیل پروژه", Colors.HEADER)
        cprint("=" * 70, Colors.HEADER)
        
        # آمار کلی
        cprint(f"\n{Colors.BOLD}📈 آمار کلی:{Colors.END}")
        cprint(f"   📁 کل فایل‌ها: {Colors.BOLD}{report.summary['total_files']}{Colors.END}")
        cprint(f"   📝 کل خطوط کد: {Colors.BOLD}{report.summary['total_lines']:,}{Colors.END}")
        cprint(f"   ⚙️  کل توابع: {Colors.BOLD}{report.summary['total_functions']:,}{Colors.END}")
        cprint(f"   🏗️  کل کلاس‌ها: {Colors.BOLD}{report.summary['total_classes']}{Colors.END}")
        cprint(f"   📦 کل ماژول‌ها: {Colors.BOLD}{report.summary['total_modules']}{Colors.END}")
        cprint(f"   🌀 میانگین پیچیدگی: {Colors.BOLD}{report.summary['avg_complexity']}{Colors.END}")
        
        # توزیع زبان‌ها
        cprint(f"\n{Colors.BOLD}🌐 توزیع زبان‌ها:{Colors.END}")
        for lang, count in sorted(report.summary['languages'].items(), 
                                   key=lambda x: x[1], reverse=True):
            bar = "█" * min(30, count // 10)
            cprint(f"   {lang:8s}: {count:5d} {Colors.DIM}{bar}{Colors.END}")
        
        # تحلیل ماژول‌ها
        cprint(f"\n{Colors.BOLD}📦 تحلیل ماژول‌ها:{Colors.END}")
        cprint(f"   {'ماژول':<15} {'فایل':<6} {'خطوط':<8} {'پیچیدگی':<10} {'Ca':<4} {'Ce':<4} {'I':<6} {'D':<6}")
        cprint("   " + "-" * 65)
        
        for name, m in sorted(report.modules.items()):
            instability_color = Colors.RED if m['instability'] > 0.8 else (
                Colors.YELLOW if m['instability'] > 0.5 else Colors.GREEN
            )
            distance_color = Colors.RED if m['distance_from_main'] > 0.4 else (
                Colors.YELLOW if m['distance_from_main'] > 0.2 else Colors.GREEN
            )
            
            cprint(
                f"   {name:<15} {m['total_files']:<6} {m['total_lines']:<8,} "
                f"{m['avg_complexity']:<10.2f} {m['afferent_coupling']:<4} "
                f"{m['efferent_coupling']:<4} "
                f"{instability_color}{m['instability']:<6.2f}{Colors.END} "
                f"{distance_color}{m['distance_from_main']:<6.2f}{Colors.END}"
            )
        
        # یافته‌ها
        cprint(f"\n{Colors.BOLD}⚠️  یافته‌ها ({len(report.findings)}):{Colors.END}")
        
        severity_colors = {
            Severity.CRITICAL.value: Colors.RED,
            Severity.HIGH.value: Colors.RED,
            Severity.MEDIUM.value: Colors.YELLOW,
            Severity.LOW.value: Colors.BLUE,
        }
        
        # گروه‌بندی بر اساس شدت
        by_severity = defaultdict(list)
        for f in report.findings:
            by_severity[f.severity].append(f)
        
        for severity in [Severity.CRITICAL.value, Severity.HIGH.value, 
                        Severity.MEDIUM.value, Severity.LOW.value]:
            findings = by_severity.get(severity, [])
            if findings:
                color = severity_colors[severity]
                cprint(f"\n   {color}{Colors.BOLD}[{severity.upper()}] ({len(findings)}){Colors.END}")
                for f in findings[:5]:  # نمایش ۵ مورد اول
                    cprint(f"      • {f.message}")
                    if f.recommendation:
                        cprint(f"        {Colors.DIM}→ {f.recommendation}{Colors.END}")
                if len(findings) > 5:
                    cprint(f"      {Colors.DIM}... و {len(findings) - 5} مورد دیگر{Colors.END}")
        
        # توصیه‌ها
        if report.recommendations:
            cprint(f"\n{Colors.BOLD}💡 توصیه‌های استراتژیک:{Colors.END}")
            for rec in report.recommendations:
                priority_color = {
                    "high": Colors.RED,
                    "medium": Colors.YELLOW,
                    "low": Colors.GREEN
                }.get(rec['priority'], Colors.END)
                cprint(f"   {priority_color}[{rec['priority'].upper()}]{Colors.END} "
                      f"{rec['category']}: {rec['message']}")
        
        cprint("\n" + "=" * 70, Colors.HEADER)

# ============================================================
# Report Generators
# ============================================================

def save_json_report(report: AnalysisReport, output_path: Path):
    """ذخیره گزارش به صورت JSON"""
    
    def convert_finding(f: Finding) -> Dict:
        return {
            "id": f.id,
            "category": f.category,
            "severity": f.severity,
            "message": f.message,
            "file": f.file,
            "line": f.line,
            "recommendation": f.recommendation
        }
    
    data = {
        "timestamp": report.timestamp,
        "project_name": report.project_name,
        "project_root": report.project_root,
        "version": report.version,
        "summary": report.summary,
        "modules": report.modules,
        "dependencies": report.dependencies,
        "findings": [convert_finding(f) for f in report.findings],
        "recommendations": report.recommendations
    }
    
    output_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8"
    )
    cprint(f"\n💾 گزارش JSON ذخیره شد: {output_path}", Colors.GREEN)

def save_html_report(report: AnalysisReport, output_path: Path):
    """ذخیره گزارش به صورت HTML"""
    html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>گزارش تحلیل پروژه {report.project_name}</title>
    <style>
        body {{ font-family: Tahoma, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat {{ background: #ecf0f1; padding: 20px; border-radius: 6px; text-align: center; }}
        .stat-value {{ font-size: 28px; font-weight: bold; color: #2980b9; }}
        .stat-label {{ color: #7f8c8d; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: right; border-bottom: 1px solid #ddd; }}
        th {{ background: #3498db; color: white; }}
        tr:hover {{ background: #f8f9fa; }}
        .critical {{ background: #e74c3c; color: white; padding: 3px 8px; border-radius: 3px; }}
        .high {{ background: #e67e22; color: white; padding: 3px 8px; border-radius: 3px; }}
        .medium {{ background: #f39c12; color: white; padding: 3px 8px; border-radius: 3px; }}
        .low {{ background: #3498db; color: white; padding: 3px 8px; border-radius: 3px; }}
        .finding {{ background: #fff; border-right: 4px solid #e74c3c; padding: 15px; margin: 10px 0; border-radius: 4px; }}
        .finding.high {{ border-right-color: #e67e22; }}
        .finding.medium {{ border-right-color: #f39c12; }}
        .finding.low {{ border-right-color: #3498db; }}
        .recommendation {{ background: #e8f5e9; padding: 15px; margin: 10px 0; border-radius: 4px; border-right: 4px solid #27ae60; }}
        .bar {{ display: inline-block; height: 10px; background: #3498db; border-radius: 5px; }}
    </style>
</head>
<body>
<div class="container">
    <h1>🔬 گزارش تحلیل پروژه {report.project_name}</h1>
    <p>تاریخ: {report.timestamp[:10]} | نسخه تحلیلگر: {report.version}</p>
    
    <h2>📈 آمار کلی</h2>
    <div class="summary">
        <div class="stat"><div class="stat-value">{report.summary['total_files']}</div><div class="stat-label">کل فایل‌ها</div></div>
        <div class="stat"><div class="stat-value">{report.summary['total_lines']:,}</div><div class="stat-label">کل خطوط</div></div>
        <div class="stat"><div class="stat-value">{report.summary['total_functions']:,}</div><div class="stat-label">توابع</div></div>
        <div class="stat"><div class="stat-value">{report.summary['total_classes']}</div><div class="stat-label">کلاس‌ها</div></div>
        <div class="stat"><div class="stat-value">{report.summary['total_modules']}</div><div class="stat-label">ماژول‌ها</div></div>
        <div class="stat"><div class="stat-value">{report.summary['avg_complexity']}</div><div class="stat-label">میانگین پیچیدگی</div></div>
    </div>
    
    <h2>📦 تحلیل ماژول‌ها</h2>
    <table>
        <tr>
            <th>ماژول</th><th>فایل</th><th>خطوط</th><th>پیچیدگی</th>
            <th>Ca</th><th>Ce</th><th>Instability</th><th>Distance</th>
        </tr>
"""
    
    for name, m in sorted(report.modules.items()):
        html += f"""
        <tr>
            <td><strong>{name}</strong></td>
            <td>{m['total_files']}</td>
            <td>{m['total_lines']:,}</td>
            <td>{m['avg_complexity']:.2f}</td>
            <td>{m['afferent_coupling']}</td>
            <td>{m['efferent_coupling']}</td>
            <td>{m['instability']:.2f}</td>
            <td>{m['distance_from_main']:.2f}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <h2>⚠️ یافته‌ها</h2>
"""
    
    for f in report.findings:
        html += f"""
    <div class="finding {f.severity}">
        <span class="{f.severity}">{f.severity.upper()}</span>
        <strong>[{f.category}]</strong> {f.message}
        <br><small>→ {f.recommendation}</small>
    </div>
"""
    
    html += """
    
    <h2>💡 توصیه‌های استراتژیک</h2>
"""
    
    for rec in report.recommendations:
        html += f"""
    <div class="recommendation">
        <strong>[{rec['priority'].upper()}] {rec['category']}:</strong> {rec['message']}
    </div>
"""
    
    html += """
</div>
</body>
</html>
"""
    
    output_path.write_text(html, encoding="utf-8")
    cprint(f"💾 گزارش HTML ذخیره شد: {output_path}", Colors.GREEN)

# ============================================================
# Main Entry Point
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description=f"{PROJECT_NAME} - Comprehensive Project Analyzer v{VERSION}"
    )
    parser.add_argument(
        "--root", type=str, default=".",
        help="مسیر ریشه پروژه (پیش‌فرض: دایرکتوری فعلی)"
    )
    parser.add_argument(
        "--modules", type=str, default="",
        help="ماژول‌های مورد تحلیل (جدا شده با کاما). مثال: ai_agents,simulation"
    )
    parser.add_argument(
        "--output", type=str, default="all",
        choices=["terminal", "json", "html", "all"],
        help="نوع خروجی"
    )
    parser.add_argument(
        "--output-dir", type=str, default=".",
        help="دایرکتوری ذخیره گزارش‌ها"
    )
    
    args = parser.parse_args()
    
    project_root = Path(args.root).resolve()
    target_modules = [m.strip() for m in args.modules.split(",") if m.strip()] or None
    
    cprint(f"\n🌱 {PROJECT_NAME} Project Analyzer v{VERSION}", Colors.BOLD)
    cprint(f"📂 ریشه پروژه: {project_root}", Colors.DIM)
    if target_modules:
        cprint(f"🎯 ماژول‌های هدف: {', '.join(target_modules)}", Colors.DIM)
    
    # اجرای تحلیل
    analyzer = ProjectAnalyzer(project_root, target_modules)
    report = analyzer.analyze()
    
    # نمایش خلاصه
    analyzer.print_summary(report)
    
    # ذخیره گزارش‌ها
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if args.output in ["json", "all"]:
        save_json_report(report, output_dir / f"analysis_report_{timestamp}.json")
    
    if args.output in ["html", "all"]:
        save_html_report(report, output_dir / f"analysis_report_{timestamp}.html")
    
    cprint(f"\n✅ تحلیل با موفقیت انجام شد!", Colors.GREEN + Colors.BOLD)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n⏹️  متوقف شد.", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        cprint(f"\n❌ خطای غیرمنتظره: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)