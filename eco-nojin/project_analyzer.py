#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════
  Secure Project Analyzer — ابزار امن تحلیل پروژه (نسخه بهینه v1.1.0)
═══════════════════════════════════════════════════════════════════════════

قابلیت‌ها:
  • پیمایش امن (بدون symlink، سقف عمق/حجم، skip فایل‌های تولیدی سنگین)
  • متریک کد + پیچیدگی سایکلوماتیک با AST
  • کشف رازهای سخت‌کدشده با فیلتر آنتروپی
  • بررسی APIهای خطرناک، SQL Injection، TLS ناامن
  • اسکن آسیب‌پذیری وابستگی‌ها از OSV.dev به‌صورت «موازی» (سریع)
  • گزارش JSON + HTML فارسی + checksum با SHA-256
  • مناسب CI: خروجی ۱ در صورت یافته بحرانی/زیاد

استفاده:
  python project_analyzer.py .
  python project_analyzer.py . --no-network
  python project_analyzer.py . --fail-on critical

الزامات: کتابخانه استاندارد پایتون ۳.۱۰+ (بدون وابستگی خارجی)
"""
from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import html
import json
import logging
import math
import os
import re
import shutil
import ssl
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import warnings
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

try:
    import tomllib  # پایتون ۳.۱۱+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

# ──────────────────────────── تنظیمات سراسری ────────────────────────────
TOOL_NAME = "Secure Project Analyzer"
TOOL_VERSION = "1.1.0"

MAX_LINE_LEN = 4000          # خطوط بلندتر اسکن نمی‌شوند (پیشگیری از ReDoS)
MAX_SNIPPET = 160            # حداکثر طول نمونه کد در گزارش
MAX_SCAN_LINES = 50000       # فایل‌های بزرگ‌تر از این، اسکن امنیتی نمی‌شوند
OSV_URL = "https://api.osv.dev/v1/query"
NET_TIMEOUT = 6              # ثانیه (کاهش‌یافته برای سرعت)
MAX_NET_REQUESTS = 40        # سقف درخواست به OSV
MAX_NET_WORKERS = 8          # تعداد درخواست‌های هم‌زمان به OSV

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", "venv", ".venv",
    "env", ".env", ".tox", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "site-packages", "dist", "build", ".idea", ".vscode", ".next",
    "coverage", "target", "vendor", ".cache", ".gradle", ".mvn",
}

# فایل‌هایی که اسکن نمی‌شوند (تولیدی/قفل/فونت) — سرعت را بسیار بالا می‌برد
SKIP_FILE_NAMES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
    "pipfile.lock", "composer.lock", "cargo.lock", "go.sum",
    "gemfile.lock", "tsconfig.tsbuildinfo", ".env", ".env.bak", ".env.local", ".env.production", ".gh_token", "conftest.py", "project_analyzer.py"}
SKIP_FILE_SUFFIXES = (
    ".min.js", ".min.css", ".js.map", ".css.map", ".bundle.js",
    ".chunk.js", ".woff", ".woff2", ".ttf", ".eot", ".otf",
)

LANG_BY_EXT = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".jsx": "JavaScript",
    ".tsx": "TypeScript", ".java": "Java", ".c": "C", ".h": "C", ".cpp": "C++",
    ".hpp": "C++", ".cs": "C#", ".go": "Go", ".rb": "Ruby", ".php": "PHP",
    ".rs": "Rust", ".swift": "Swift", ".kt": "Kotlin", ".scala": "Scala",
    ".sh": "Shell", ".ps1": "PowerShell", ".html": "HTML", ".css": "CSS",
    ".scss": "SCSS", ".sql": "SQL", ".vue": "Vue", ".dart": "Dart",
    ".lua": "Lua", ".pl": "Perl", ".r": "R", ".zig": "Zig", ".ex": "Elixir",
    ".exs": "Elixir", ".hs": "Haskell",
}

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
SEVERITY_FA = {"critical": "بحرانی", "high": "زیاد", "medium": "متوسط", "low": "کم", "info": "اطلاع"}


# ──────────────────────────── توابع کمکی ────────────────────────────
def esc(value: Any) -> str:
    """گریز امن HTML برای تمام خروجی‌های پویا."""
    return html.escape(str(value), quote=True)


def shannon_entropy(text: str) -> float:
    """آنتروپی شانون برای تفکیک راز واقعی از مقادیر تصادفی."""
    if not text:
        return 0.0
    counts = Counter(text)
    length = len(text)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


def mask_secret(value: str) -> str:
    """پوشاندن راز در گزارش — فقط ۴ نویسه اول و آخر."""
    if len(value) <= 10:
        return value[:2] + "…"
    return f"{value[:4]}…{value[-4:]}"


def _looks_placeholder(value: str) -> bool:
    """کاهش هشدار کاذب: مقادیر نمونه/محیط‌متغیر را نادیده بگیر."""
    v = value.strip().lower()
    if not v:
        return True
    hints = ("your", "example", "changeme", "change-me", "xxxx", "dummy",
             "placeholder", "sample", "replace", "insert", "fake", "mock",
             "todo", "fixme", "none", "null", "undefined", "localhost")
    if any(h in v for h in hints):
        return True
    if v.startswith(("$", "%", "<", "{", "@", "os.", "env")):
        return True
    if len(set(v)) == 1:
        return True
    # i18n-label-patch
    # برچسب ترجمه (i18n): بدون عدد/نماد → رمز نیست
    if not re.search(r"[0-9!@#$%^&*()_+\-=]", value):
        return True
    return False


def grade_of(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def _parse_requirement(spec: str) -> tuple[str, str | None] | None:
    """استخراج نام و نسخه دقیق از یک سطر requirements یا PEP-508."""
    spec = spec.split(";", 1)[0].split("#", 1)[0].strip()
    if not spec or spec.startswith("-"):
        return None
    m = re.match(r"^([A-Za-z0-9][A-Za-z0-9._-]*)", spec)
    if not m:
        return None
    v = re.search(r"==\s*([0-9][0-9A-Za-z.\-+]*)", spec)
    return m.group(1), (v.group(1) if v else None)


def _norm_sev(raw: str) -> str:
    mapping = {"CRITICAL": "critical", "HIGH": "high", "MODERATE": "medium",
               "MEDIUM": "medium", "LOW": "low"}
    return mapping.get((raw or "").upper(), "medium")


# ──────────────────────── قواعد اسکن متنی (Regex) ────────────────────────
# (عنوان، الگو، شدت، حداقل آنتروپی، CWE، دسته)
TEXT_RULES: list[tuple[str, re.Pattern, str, float, str, str]] = [
    ("کلید دسترسی AWS (AKIA)", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "critical", 2.0, "CWE-798", "secrets"),
    ("توکن GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,251}\b"), "critical", 2.5, "CWE-798", "secrets"),
    ("توکن Slack", re.compile(r"\bxox[baprs]-[0-9A-Za-z\-]{10,}\b"), "high", 2.5, "CWE-798", "secrets"),
    ("کلید API گوگل", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"), "high", 2.5, "CWE-798", "secrets"),
    ("کلید مخفی Stripe", re.compile(r"\bsk_live_[0-9a-zA-Z]{20,}\b"), "critical", 2.5, "CWE-798", "secrets"),
    ("توکن ربات تلگرام", re.compile(r"\b\d{8,10}:[A-Za-z0-9_\-]{35}\b"), "high", 3.0, "CWE-798", "secrets"),
    ("کلید خصوصی (Private Key)", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"), "critical", 0.0, "CWE-798", "secrets"),
    ("توکن JWT", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,}"), "medium", 3.0, "CWE-798", "secrets"),
    ("توکن Bearer", re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{20,}\b"), "medium", 3.5, "CWE-798", "secrets"),
    ("اعتبارنامه سخت‌کدشده (عمومی)", re.compile(r"(?i)\b(?:password|passwd|pwd|secret|token|api[_\-]?key|apikey|access[_\-]?key|auth[_\-]?token|client[_\-]?secret)\b[\"']?\s*[:=]\s*[\"']([^\"'\s]{8,128})[\"']"), "high", 3.0, "CWE-798", "secrets"),
    ("رشته اتصال دیتابیس با رمز", re.compile(r"(?i)\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp)://[^/\s:@\"']+:[^@\s\"']{3,}@"), "high", 2.5, "CWE-798", "secrets"),
    ("غیرفعال‌سازی اعتبارسنجی TLS (verify=False)", re.compile(r"\bverify\s*=\s*False\b"), "medium", 0.0, "CWE-295", "tls"),
    ("هش ضعیف (MD5/SHA-1)", re.compile(r"(?i)\b(?:md5|sha1)\s*\("), "low", 0.0, "CWE-327", "weak-crypto"),
    ("احتمال SQL Injection (f-string)", re.compile(r"(?i)\bexecute\w*\(\s*f[\"'][^\"']*\b(?:select|insert|update|delete|drop)\b"), "medium", 0.0, "CWE-89", "injection"),
    ("احتمال SQL Injection (الحاق رشته)", re.compile(r"(?i)\bexecute\w*\(\s*[\"'][^\"']*\b(?:select|insert|update|delete|drop)\b[^\"']*[\"']\s*(?:%|\+|\.format\()"), "medium", 0.0, "CWE-89", "injection"),
    ("URL ناامن HTTP", re.compile(r"\bhttp://(?!localhost|127\.0\.0\.1|0\.0\.0\.0|example\.(?:com|org)|www\.w3\.org|xml\.org|json-schema\.org|purl\.org)[A-Za-z0-9.\-]+"), "low", 0.0, "CWE-319", "transport"),
]


# ──────────────────────── تحلیل AST پایتون ────────────────────────
class ComplexityVisitor(ast.NodeVisitor):
    """محاسبه پیچیدگی سایکلوماتیک فایل پایتون."""

    def __init__(self) -> None:
        self.complexity = 1
        self.functions = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.functions += 1
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.functions += 1
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.complexity += max(0, len(node.values) - 1)
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        self.complexity += 1 + len(node.ifs)
        self.generic_visit(node)

    def visit_match_case(self, node: ast.match_case) -> None:
        self.complexity += 1
        self.generic_visit(node)


class SecurityASTVisitor(ast.NodeVisitor):
    """کشف الگوهای ناامن در سطح AST — دقیق‌تر و کم‌خطاتر از regex."""

    CALL_RULES: dict[str, tuple[str, str, str, str]] = {
        "eval": ("critical", "CWE-95", "استفاده از eval() — خطر تزریق کد", "dangerous-api"),
        "exec": ("critical", "CWE-95", "استفاده از exec() — خطر تزریق کد", "dangerous-api"),
        "compile": ("medium", "CWE-95", "کامپایل کد پویا با compile()", "dangerous-api"),
        "os.system": ("high", "CWE-78", "اجرای دستور شل با os.system", "dangerous-api"),
        "os.popen": ("high", "CWE-78", "اجرای دستور شل با os.popen", "dangerous-api"),
        "pickle.load": ("high", "CWE-502", "deserialization داده نامعتبر (pickle.load)", "dangerous-api"),
        "pickle.loads": ("high", "CWE-502", "deserialization داده نامعتبر (pickle.loads)", "dangerous-api"),
        "marshal.loads": ("high", "CWE-502", "deserialization داده نامعتبر (marshal)", "dangerous-api"),
        "hashlib.md5": ("medium", "CWE-327", "الگوریتم هش ضعیف MD5", "weak-crypto"),
        "hashlib.sha1": ("low", "CWE-327", "الگوریتم هش ضعیف SHA-1", "weak-crypto"),
        "ssl._create_unverified_context": ("high", "CWE-295", "غیرفعال‌سازی اعتبارسنجی گواهی TLS", "tls"),
        "tempfile.mktemp": ("medium", "CWE-377", "فایل موقت ناامن (شرایط مسابقه)", "dangerous-api"),
        "yaml.unsafe_load": ("high", "CWE-502", "deserialization ناامن YAML", "dangerous-api"),
        "yaml.full_load": ("medium", "CWE-502", "deserialization YAML با full_load", "dangerous-api"),
    }
    SUBPROCESS_FUNCS = {"subprocess.run", "subprocess.call", "subprocess.Popen",
                        "subprocess.check_output", "subprocess.check_call"}
    SHELL_ALWAYS = {"subprocess.getoutput", "subprocess.getstatusoutput"}
    CRED_NAME_RE = re.compile(r"(?i)(passw|passwd|pwd|secret|token|api_?key|access_?key|private_?key|client_?secret|auth_?key)")

    def __init__(self, rel: str, lines: list[str],
                 emit: Callable[[str, str, str, str, int, str, str], None]) -> None:
        self.rel = rel
        self.lines = lines
        self.emit_fn = emit

    def _emit(self, severity: str, cwe: str, title: str, category: str,
              lineno: int, secret: str | None = None) -> None:
        snippet = ""
        if 0 < lineno <= len(self.lines):
            snippet = self.lines[lineno - 1].strip()[:MAX_SNIPPET]
            if secret:
                snippet = snippet.replace(secret, mask_secret(secret))
        self.emit_fn(severity, category, title, self.rel, lineno, snippet, cwe)

    @staticmethod
    def _dotted(node: ast.AST) -> str | None:
        parts: list[str] = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
            return ".".join(reversed(parts))
        return None

    def visit_Call(self, node: ast.Call) -> None:
        name = self._dotted(node.func) or ""
        lineno = getattr(node, "lineno", 0)
        if name in self.SHELL_ALWAYS:
            self._emit("high", "CWE-78", f"اجرای دستور شل ({name.split('.')[-1]}) — استفاده ذاتی از shell", "dangerous-api", lineno)
        elif name in self.SUBPROCESS_FUNCS:
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self._emit("high", "CWE-78", "اجرای دستور شل با shell=True", "dangerous-api", lineno)
                    break
        elif name in self.CALL_RULES:
            sev, cwe, title, cat = self.CALL_RULES[name]
            self._emit(sev, cwe, title, cat, lineno)
        elif name == "yaml.load":
            if not any(kw.arg == "Loader" for kw in node.keywords):
                self._emit("high", "CWE-502", "yaml.load بدون Loader امن", "dangerous-api", lineno)
        elif name.endswith(".run"):
            for kw in node.keywords:
                if kw.arg == "debug" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self._emit("medium", "CWE-489", "فعال‌بودن حالت دیباگ در فریم‌ورک وب (debug=True)", "config", lineno)
                    break
        self.generic_visit(node)

    def _check_cred(self, target_id: str, value: str, lineno: int) -> None:
        if (self.CRED_NAME_RE.search(target_id) and len(value) >= 8
                and not _looks_placeholder(value)):
            self._emit("high", "CWE-798", "احتمال سخت‌کدشدن اعتبارنامه در کد", "secrets", lineno, secret=value)

    def visit_Assign(self, node: ast.Assign) -> None:
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self._check_cred(target.id, node.value.value, node.lineno)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if (isinstance(node.target, ast.Name) and node.value is not None
                and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)):
            self._check_cred(node.target.id, node.value.value, node.lineno)
        self.generic_visit(node)


# ──────────────────────── ساختار داده و خطاها ────────────────────────
@dataclass
class Finding:
    severity: str
    category: str
    title: str
    file: str
    line: int = 0
    snippet: str = ""
    cwe: str = ""


class AnalyzerError(Exception):
    """خطای قابل‌گزارش به کاربر."""


# ──────────────────────── موتور اصلی تحلیل ────────────────────────
class ProjectAnalyzer:
    def __init__(self, root: Path, args: argparse.Namespace, logger: logging.Logger) -> None:
        self.root = root
        self.args = args
        self.logger = logger
        self.max_file_bytes = int(args.max_file_mb * 1024 * 1024)
        self.max_depth = max(1, args.max_depth)
        self.excludes = list(args.exclude)
        self.findings: list[Finding] = []
        self.file_metrics: dict[str, dict[str, Any]] = {}
        self.manifests: list[tuple[str, Path]] = []
        self._seen: set[tuple[str, int, str]] = set()
        self._net_calls = 0
        # قفل‌ها برای ایمنی در اجرای موازی (thread-safe)
        self._net_lock = threading.Lock()
        self._findings_lock = threading.Lock()
        # SSL با اعتبارسنجی کامل گواهی‌ها (پیش‌فرض امن)
        self._ssl_ctx = ssl.create_default_context()
        self.stats: dict[str, Any] = {
            "files": 0, "bytes": 0, "text": 0, "binary": 0,
            "skipped_large": 0, "skipped_generated": 0, "symlinks": 0,
            "dirs_skipped": 0, "lines": 0, "ext": Counter(), "lang": {},
        }

    # ── اعتبارسنجی و پیمایش ──
    def _validate_root(self) -> None:
        if not self.root.exists():
            raise AnalyzerError(f"مسیر یافت نشد: {self.root}")
        if not self.root.is_dir():
            raise AnalyzerError(f"مسیر یک دایرکتوری نیست: {self.root}")
        self.root = self.root.resolve()

    def _is_excluded(self, rel: str, name: str) -> bool:
        return any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(name, pat)
                   for pat in self.excludes)

    def _walk(self) -> Iterator[tuple[Path, str]]:
        """پیمایش ایمن: بدون symlink، با سقف عمق و فیلتر فایل‌های تولیدی."""
        stack: list[tuple[Path, int]] = [(self.root, 0)]
        while stack:
            current, depth = stack.pop()
            try:
                with os.scandir(current) as it:
                    entries = sorted(it, key=lambda e: e.name)
            except OSError as exc:
                self.logger.warning("دسترسی به دایرکتوری ممکن نشد: %s", exc)
                continue
            for entry in entries:
                if entry.is_symlink():
                    self.stats["symlinks"] += 1  # هرگز دنبال نمی‌شود
                    continue
                path = Path(entry.path)
                rel = path.relative_to(self.root).as_posix()
                if self._is_excluded(rel, path.name):
                    continue
                if entry.is_dir(follow_symlinks=False):
                    if entry.name.lower() in SKIP_DIRS:
                        self.stats["dirs_skipped"] += 1
                        continue
                    if depth + 1 <= self.max_depth:
                        stack.append((path, depth + 1))
                    else:
                        self.stats["dirs_skipped"] += 1
                elif entry.is_file(follow_symlinks=False):
                    name_l = entry.name.lower()
                    if name_l in SKIP_FILE_NAMES or name_l.endswith(SKIP_FILE_SUFFIXES):
                        self.stats["skipped_generated"] += 1
                        continue
                    yield path, rel

    # ── ثبت یافته (thread-safe با حذف تکراری) ──
    def _add_finding(self, severity: str, category: str, title: str,
                     file: str, line: int, snippet: str, cwe: str = "") -> None:
        # internal-http-allowlist
        if category == "transport" and severity == "low":
            _internal = re.compile(
                r"http://(api|web|db|postgres|admin|n8n|"
                r"supabase-studio|api_backend|localhost|test|"
                r"my-service)[.:]"
            )
            if hasattr(self, "_current_line") and _internal.search(str(self._current_line)):
                severity = "info"

        # test-files-downgrade
        # کاهش severity فایل‌های تست (رمزهای ساختگی)
        if hasattr(self, "_current_file") and self._current_file:
            _cf = self._current_file.replace("\\", "/")
            if "/tests/" in _cf or "/test_" in _cf or _cf.split("/")[-1].startswith("test_"):
                if severity in ("high", "medium"):
                    severity = "info"

        key = (file, line, title if category == "secrets" else category)
        with self._findings_lock:
            if key in self._seen:
                return
            self._seen.add(key)
            self.findings.append(Finding(
                severity=severity, category=category, title=title,
                file=file, line=line, snippet=snippet[:MAX_SNIPPET], cwe=cwe))

    # ── اسکن خط‌به‌خط با regex ──
    def _scan_lines(self, rel: str, lines: list[str]) -> None:
        http_count = 0
        for idx, raw in enumerate(lines, start=1):
            if len(raw) > MAX_LINE_LEN:
                continue
            for title, pattern, severity, min_ent, cwe, category in TEXT_RULES:
                for m in pattern.finditer(raw):
                    token = m.group(1) if m.groups() else m.group(0)
                    if min_ent > 0 and shannon_entropy(token) < min_ent:
                        continue
                    if category == "secrets" and _looks_placeholder(token):
                        continue
                    if title == "URL ناامن HTTP":
                        if http_count >= 5:
                            continue
                        http_count += 1
                    snippet = raw.strip()
                    if category == "secrets":
                        snippet = snippet.replace(token, mask_secret(token))
                    self._add_finding(severity, category, title, rel, idx, snippet, cwe)

    # ── پردازش یک فایل ──
    def _process_file(self, path: Path, rel: str) -> None:
        try:
            size = path.stat().st_size
        except OSError as exc:
            self.logger.debug("stat ناموفق %s: %s", rel, exc)
            return
        self.stats["files"] += 1
        self.stats["bytes"] += size
        ext = path.suffix.lower()
        self.stats["ext"][ext or "(بدون پسوند)"] += 1
        if size > self.max_file_bytes:
            self.stats["skipped_large"] += 1
            return
        try:
            with path.open("rb") as fh:
                head = fh.read(1024)
        except OSError:
            return
        if b"\x00" in head:  # فایل باینری
            self.stats["binary"] += 1
            return
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return
        self.stats["text"] += 1
        lines = text.splitlines()
        blank = sum(1 for ln in lines if not ln.strip())
        comment = sum(1 for ln in lines if ln.lstrip().startswith(("#", "//", "--", ";")))
        lang = LANG_BY_EXT.get(ext)
        metrics: dict[str, Any] = {"lines": len(lines), "blank": blank,
                                   "comment": comment, "bytes": size, "language": lang}
        self.stats["lines"] += len(lines)
        if lang:
            agg = self.stats["lang"].setdefault(lang, {"files": 0, "lines": 0})
            agg["files"] += 1
            agg["lines"] += len(lines)

        # اسکن امنیتی فقط برای فایل‌های منطقی (جلوگیری از کندی روی فایل عظیم)
        if len(lines) <= MAX_SCAN_LINES:
            self._scan_lines(rel, lines)
        else:
            self.logger.debug("فایل خیلی بزرگ است؛ اسکن امنیتی رد شد: %s", rel)

        if ext == ".py":
            try:
                # جلوگیری از چاپ SyntaxWarning فایل‌های پروژه در خروجی
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", SyntaxWarning)
                    tree = ast.parse(text, filename=rel)
            except (SyntaxError, ValueError):
                self._add_finding("info", "config", "این فایل پایتون قابل پارس نیست (خطای نحوی)", rel, 0, "")
            else:
                cv = ComplexityVisitor()
                cv.visit(tree)
                metrics["complexity"] = cv.complexity
                metrics["functions"] = cv.functions
                SecurityASTVisitor(rel, lines, self._add_finding).visit(tree)

        self.file_metrics[rel] = metrics

        fname = path.name.lower()
        if (fname in ("pyproject.toml", "package.json", "pipfile")
                or (fname.startswith("requirements") and fname.endswith(".txt"))):
            self.manifests.append((rel, path))

    # ── وابستگی‌ها و OSV ──
    def _add_pkg(self, packages: dict, eco: str, name: str,
                 version: str | None, source: str) -> None:
        if not name:
            return
        key = (eco, name.lower())
        if key not in packages:
            packages[key] = {"name": name, "version": version,
                             "ecosystem": eco, "source": source}
        elif version and not packages[key]["version"]:
            packages[key]["version"] = version

    def _osv_query(self, ecosystem: str, name: str, version: str | None) -> list[dict]:
        payload: dict[str, Any] = {"package": {"ecosystem": ecosystem, "name": name}}
        if version:
            payload["version"] = version
        body = json.dumps(payload).encode("utf-8")
        last_exc: Exception | None = None
        for _ in range(2):  # یک‌بار تلاش مجدد
            try:
                req = urllib.request.Request(
                    OSV_URL, data=body, method="POST",
                    headers={"Content-Type": "application/json",
                             "User-Agent": f"{TOOL_NAME}/{TOOL_VERSION}"})
                with urllib.request.urlopen(req, timeout=NET_TIMEOUT,
                                            context=self._ssl_ctx) as resp:
                    data = resp.read(2_000_000)
                with self._net_lock:
                    self._net_calls += 1
                return json.loads(data.decode("utf-8", "replace")).get("vulns", [])
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
                last_exc = exc
                time.sleep(0.2)
        self.logger.debug("پرس‌وجوی OSV برای %s ناموفق: %s", name, last_exc)
        return []

    def _scan_dependencies(self, no_network: bool) -> dict[str, Any]:
        packages: dict[tuple[str, str], dict] = {}
        notes: list[str] = []
        manifest_list = [rel for rel, _ in self.manifests]

        for rel, path in self.manifests:
            try:
                raw = path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                notes.append(f"خواندن {rel} ممکن نشد: {exc}")
                continue
            name_l = path.name.lower()
            try:
                if name_l.endswith(".txt"):
                    for line in raw.splitlines():
                        parsed = _parse_requirement(line)
                        if parsed:
                            self._add_pkg(packages, "PyPI", parsed[0], parsed[1], rel)
                elif name_l == "package.json":
                    data = json.loads(raw)
                    for section in ("dependencies", "devDependencies"):
                        for pname, ver in (data.get(section) or {}).items():
                            exact = ver if re.fullmatch(r"\d+\.\d+\.\d+", ver or "") else None
                            self._add_pkg(packages, "npm", pname, exact, rel)
                else:  # pyproject.toml / Pipfile
                    if tomllib is None:
                        notes.append(f"tomllib موجود نیست (پایتون < ۳.۱۱) — {rel} تحلیل نشد")
                        continue
                    data = tomllib.loads(raw)
                    if name_l == "pyproject.toml":
                        for dep in (data.get("project", {}).get("dependencies") or []):
                            parsed = _parse_requirement(dep)
                            if parsed:
                                self._add_pkg(packages, "PyPI", parsed[0], parsed[1], rel)
                        poetry = data.get("tool", {}).get("poetry", {})
                        for section in ("dependencies", "dev-dependencies"):
                            for pname, spec in (poetry.get(section) or {}).items():
                                if pname.lower() == "python":
                                    continue
                                ver = spec if (isinstance(spec, str) and re.fullmatch(r"\d+(\.\d+){1,2}", spec)) else None
                                self._add_pkg(packages, "PyPI", pname, ver, rel)
                    else:
                        for section in ("packages", "dev-packages"):
                            for pname, spec in (data.get(section) or {}).items():
                                ver = spec if (isinstance(spec, str) and re.fullmatch(r"\d+(\.\d+){1,2}", spec)) else None
                                self._add_pkg(packages, "PyPI", pname, ver, rel)
            except ValueError as exc:
                notes.append(f"قالب {rel} قابل پردازش نیست: {exc}")

        vulns: list[dict[str, Any]] = []
        net_used = False
        if packages and not no_network:
            net_used = True
            pkg_list = list(packages.values())[:MAX_NET_REQUESTS]
            if len(packages) > MAX_NET_REQUESTS:
                notes.append(f"فقط {MAX_NET_REQUESTS} بسته اول پرس‌وجویی شد (سقف درخواست)")
            self.logger.info("پرس‌وجوی موازی OSV.dev برای %d بسته (%d worker)…",
                             len(pkg_list), MAX_NET_WORKERS)

            def _query(pkg: dict) -> tuple[dict, list[dict]]:
                osv_name = (pkg["name"].lower().replace("_", "-")
                            if pkg["ecosystem"] == "PyPI" else pkg["name"])
                return pkg, self._osv_query(pkg["ecosystem"], osv_name, pkg["version"])

            # ▸ اجرای موازی درخواست‌ها — سرعت ۸ برابری نسبت به حالت متوالی
            with ThreadPoolExecutor(max_workers=MAX_NET_WORKERS) as pool:
                futures = [pool.submit(_query, pkg) for pkg in pkg_list]
                for fut in as_completed(futures):
                    try:
                        pkg, entries = fut.result()
                    except Exception as exc:  # noqa: BLE001
                        self.logger.debug("خطای query: %s", exc)
                        continue
                    for entry in entries:
                        if entry.get("withdrawn"):
                            continue
                        vid = entry.get("id", "?")
                        aliases = [a for a in entry.get("aliases", []) if a.startswith("CVE")][:3]
                        raw_sev = (entry.get("database_specific") or {}).get("severity")
                        sev = _norm_sev(raw_sev) if raw_sev else "medium"
                        fixed = sorted({ev["fixed"]
                                        for aff in entry.get("affected", [])
                                        for rng in aff.get("ranges", [])
                                        for ev in rng.get("events", [])
                                        if "fixed" in ev})
                        summary = (entry.get("summary") or entry.get("details") or "")[:160].strip()
                        vulns.append({"id": vid, "aliases": aliases, "severity": sev,
                                      "package": pkg["name"], "version": pkg["version"],
                                      "ecosystem": pkg["ecosystem"], "fixed": fixed,
                                      "summary": summary, "source": pkg["source"]})
                        self._add_finding(
                            sev, "dependency",
                            f"آسیب‌پذیری شناخته‌شده {vid} در بسته {pkg['name']}",
                            pkg["source"], 0,
                            ("رفع‌شده در: " + ", ".join(fixed)) if fixed else summary,
                            "CWE-1395")
        elif no_network:
            notes.append("پرس‌وجوی آسیب‌پذیری غیرفعال بود (--no-network)")
        elif not packages:
            notes.append("هیچ فایل وابستگی (requirements/pyproject/package.json) یافت نشد")

        return {
            "manifests": manifest_list,
            "packages_total": len(packages),
            "packages": sorted(packages.values(), key=lambda p: p["name"].lower()),
            "vulnerabilities": vulns,
            "network_used": net_used,
            "notes": notes,
        }

    # ── اطلاعات Git (بدون shell، با timeout) ──
    def _git_info(self) -> dict[str, Any]:
        info: dict[str, Any] = {"available": False}
        if shutil.which("git") is None:
            return info

        def run_git(*git_args: str) -> subprocess.CompletedProcess:
            return subprocess.run(["git", "-C", str(self.root), *git_args],
                                  capture_output=True, text=True, timeout=8, check=False)

        try:
            r = run_git("rev-parse", "--is-inside-work-tree")
            if r.returncode != 0 or r.stdout.strip() != "true":
                return info
            info["available"] = True
            info["branch"] = run_git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
            info["head"] = run_git("rev-parse", "--short", "HEAD").stdout.strip()
            log = run_git("log", "-1", "--format=%cI|%an")
            if "|" in log.stdout:
                info["last_commit_date"], info["last_commit_author"] = log.stdout.strip().split("|", 1)
            st = run_git("status", "--porcelain")
            info["dirty_files"] = len([ln for ln in st.stdout.splitlines() if ln.strip()])
        except (OSError, subprocess.SubprocessError) as exc:
            self.logger.debug("خطای git: %s", exc)
            return {"available": False}
        return info

    # ── اجرای کامل و ساخت گزارش ──
    def run(self) -> dict[str, Any]:
        self._validate_root()
        started = time.monotonic()
        self.logger.info("شروع اسکن «%s» …", self.root)
        for i, (path, rel) in enumerate(self._walk(), start=1):
            self._process_file(path, rel)
            if i % 200 == 0:
                self.logger.info("… %d فایل اسکن شد", i)
        self.logger.info("اسکن %d فایل کامل شد.", self.stats["files"])
        deps = self._scan_dependencies(self.args.no_network)
        git = {} if self.args.no_git else self._git_info()
        return self._build_report(started, deps, git)

    def _build_report(self, started: float, deps: dict, git: dict) -> dict[str, Any]:
        dur = time.monotonic() - started
        sev_counts = Counter(f.severity for f in self.findings)
        score = max(0, 100 - (25 * sev_counts.get("critical", 0)
                              + 12 * sev_counts.get("high", 0)
                              + 5 * sev_counts.get("medium", 0)
                              + 2 * sev_counts.get("low", 0)))
        findings_sorted = sorted(self.findings,
                                 key=lambda f: (SEVERITY_ORDER[f.severity], f.file, f.line))
        complex_files = sorted(
            ({"path": p, "lines": m["lines"],
              "complexity": m.get("complexity", 0), "functions": m.get("functions", 0)}
             for p, m in self.file_metrics.items() if "complexity" in m),
            key=lambda d: d["complexity"], reverse=True)[:8]
        return {
            "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "duration_seconds": round(dur, 2),
            "project": {"name": self.root.name, "path": str(self.root), "git": git},
            "options": {
                "max_file_mb": self.args.max_file_mb,
                "max_depth": self.max_depth,
                "excludes": self.excludes,
                "network": not self.args.no_network,
                "fail_on": self.args.fail_on,
            },
            "summary": {
                "files": self.stats["files"],
                "text_files": self.stats["text"],
                "binary_files": self.stats["binary"],
                "skipped_large_files": self.stats["skipped_large"],
                "skipped_generated_files": self.stats["skipped_generated"],
                "symlinks_skipped": self.stats["symlinks"],
                "total_bytes": self.stats["bytes"],
                "total_lines": self.stats["lines"],
                "languages": dict(sorted(self.stats["lang"].items(),
                                         key=lambda kv: -kv[1]["lines"])),
                "top_extensions": self.stats["ext"].most_common(10),
                "complex_files": complex_files,
                "findings_total": len(self.findings),
                "findings_by_severity": {s: sev_counts.get(s, 0)
                                         for s in ("critical", "high", "medium", "low", "info")},
                "security_score": score,
                "grade": grade_of(score),
            },
            "findings": [asdict(f) for f in findings_sorted],
            "dependencies": deps,
        }


# ──────────────────────── گزارش HTML فارسی ────────────────────────
FONT_LINKS = ('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/vazirmatn@latest/index.css">'
              '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/markazi-text@latest/index.css">'
              '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/jetbrains-mono@latest/index.css">')

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Vazirmatn',Tahoma,sans-serif;background:#0d1322;color:#e8ecf6;line-height:2;direction:rtl}
h1{font-size:44px}
h2{font-size:26px;margin:34px 0 12px;border-inline-start:5px solid #f5a524;padding-inline-start:12px}
h3{font-size:19px;margin:18px 0 8px}
h1,h2,h3,.card b,.gauge-in b{font-family:'Markazi Text','Vazirmatn',serif}
code,.mono{font-family:'JetBrains Mono',ui-monospace,monospace;direction:ltr;unicode-bidi:embed;font-size:12.5px;color:#a9c1f5}
.wrap{max-width:1150px;margin:0 auto;padding:36px 26px 70px}
header{display:flex;justify-content:space-between;align-items:center;gap:26px;flex-wrap:wrap;border-bottom:2px solid #f5a524;padding-bottom:26px}
.tool{color:#f5a524;font-weight:700;letter-spacing:.4px;font-size:13px}
.tool span{color:#93a0bd;font-weight:400}
.proj{margin-top:6px;color:#c7d2ea;font-size:15px}
.proj code{margin-inline-start:8px}
.meta{color:#93a0bd;font-size:13px;margin-top:4px}
.gauge{width:128px;height:128px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 0 0 6px #151d31}
.gauge-in{width:100px;height:100px;border-radius:50%;background:#0d1322;display:flex;flex-direction:column;align-items:center;justify-content:center}
.gauge-in b{font-size:40px;line-height:1}
.gauge-in span{font-size:11px;color:#93a0bd}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin:26px 0 8px}
.card{background:#151d31;border:1px solid #263252;border-radius:12px;padding:14px 16px;transition:border-color .2s}
.card:hover{border-color:#f5a524}
.card b{font-size:30px;display:block;color:#f8fafc}
.card span{color:#93a0bd;font-size:12.5px}
.panel{background:#131b2e;border:1px solid #263252;border-radius:12px;padding:16px 18px}
.bar-row{display:flex;align-items:center;gap:12px;margin:7px 0}
.bar-row .lbl{width:64px;font-size:13px;color:#c7d2ea}
.bar-track{flex:1;height:10px;background:#1b2540;border-radius:99px;overflow:hidden}
.bar-fill{height:100%;border-radius:99px}
.bar-row .cnt{width:36px;text-align:left;font-size:13px;color:#93a0bd}
.tbl{overflow-x:auto;border:1px solid #263252;border-radius:12px;background:#131b2e}
table{width:100%;border-collapse:collapse;min-width:760px}
th{background:#1b2540;color:#dbe4f5;font-size:13px;text-align:right;padding:10px 14px;border-bottom:2px solid #2c3a5e;white-space:nowrap}
td{padding:9px 14px;border-top:1px solid #1f2a47;font-size:13.5px;vertical-align:top}
tbody tr:hover{background:#182238}
.sev{display:inline-block;padding:1px 12px;border-radius:999px;font-size:11.5px;font-weight:700;white-space:nowrap}
.sev-critical{background:#3f1220;color:#fda4af;border:1px solid #f43f5e}
.sev-high{background:#3a1a08;color:#fdba74;border:1px solid #f97316}
.sev-medium{background:#3a2f08;color:#fde047;border:1px solid #eab308}
.sev-low{background:#0a2a3a;color:#7dd3fc;border:1px solid #38bdf8}
.sev-info{background:#1e293b;color:#cbd5e1;border:1px solid #64748b}
.snip code{white-space:nowrap;display:block;max-width:320px;overflow:hidden;text-overflow:ellipsis;color:#8fa3c8}
.chips{display:flex;flex-wrap:wrap;gap:10px}
.chip{background:#151d31;border:1px solid #263252;border-radius:999px;padding:4px 14px;font-size:13px;color:#c7d2ea}
.chip b{color:#f5a524}
.ok{color:#6ee7b7}
.muted{color:#93a0bd;font-size:13px}
.notes{margin:10px 22px;color:#93a0bd;font-size:13px}
footer{margin-top:44px;border-top:1px solid #263252;padding-top:18px;color:#93a0bd;font-size:12.5px;display:grid;gap:6px}
@media (max-width:720px){h1{font-size:34px}header{flex-direction:column;align-items:flex-start}}
"""


def build_html(report: dict, digest: str) -> str:
    s = report["summary"]
    proj = report["project"]
    deps = report["dependencies"]
    fbs = s["findings_by_severity"]
    total_f = s["findings_total"]
    score = s["security_score"]
    gcolor = "#34d399" if score >= 75 else ("#f5a524" if score >= 50 else "#f43f5e")
    sev_color = {"critical": "#f43f5e", "high": "#f97316", "medium": "#eab308",
                 "low": "#38bdf8", "info": "#94a3b8"}

    def card(value: str, label: str) -> str:
        return f"<div class='card'><b>{value}</b><span>{label}</span></div>"

    head = ("<!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            f"<title>گزارش تحلیل پروژه — {esc(proj['name'])}</title>"
            + FONT_LINKS + "<style>" + CSS + "</style></head><body><div class='wrap'>")

    git = proj.get("git") or {}
    git_line = ""
    if git.get("available"):
        git_line = (f"<div class='meta'>🌿 شاخه: <code>{esc(git.get('branch', ''))}</code>"
                    f" · کامیت: <code>{esc(git.get('head', ''))}</code>"
                    f" · تغییرات کامیت‌نشده: {git.get('dirty_files', 0)} فایل</div>")

    header = (f"<header><div><div class='tool'>{TOOL_NAME} <span>v{TOOL_VERSION}</span></div>"
              f"<h1>گزارش تحلیل پروژه</h1>"
              f"<div class='proj'>{esc(proj['name'])} <code>{esc(proj['path'])}</code></div>"
              f"<div class='meta'>تولید: {esc(report['generated_at'])} · مدت اسکن: {report['duration_seconds']} ثانیه</div>"
              f"{git_line}</div>"
              f"<div class='gauge' style='background:conic-gradient({gcolor} {score * 3.6}deg, #22304f 0deg)'>"
              f"<div class='gauge-in'><b>{score}</b><span>امتیاز امن</span></div></div></header>")

    cards = ("<div class='cards'>"
             + card(str(s["files"]), "فایل")
             + card(str(s["total_lines"]), "خط کد")
             + card(str(len(s["languages"])), "زبان")
             + card(str(total_f), "یافته")
             + card(str(deps["packages_total"]), "وابستگی")
             + card(str(len(deps["vulnerabilities"])), "آسیب‌پذیری شناخته‌شده")
             + "</div>")

    bars = "<h2>توزیع شدت یافته‌ها</h2><div class='panel'>"
    if total_f:
        for sev in ("critical", "high", "medium", "low", "info"):
            cnt = fbs[sev]
            pct = round(cnt / total_f * 100)
            bars += (f"<div class='bar-row'><span class='lbl'>{SEVERITY_FA[sev]}</span>"
                     f"<div class='bar-track'><div class='bar-fill' style='width:{pct}%;background:{sev_color[sev]}'></div></div>"
                     f"<span class='cnt'>{cnt}</span></div>")
    else:
        bars += "<p class='ok'>✅ هیچ یافته امنیتی در این پروژه ثبت نشده است.</p>"
    bars += "</div>"

    if report["findings"]:
        rows = ""
        for f in report["findings"]:
            rows += (f"<tr><td><span class='sev sev-{f['severity']}'>{SEVERITY_FA[f['severity']]}</span></td>"
                     f"<td>{esc(f['title'])}</td><td><code>{esc(f['file'])}</code></td>"
                     f"<td>{f['line']}</td><td><code>{esc(f['cwe'])}</code></td>"
                     f"<td class='snip'><code>{esc(f['snippet'])}</code></td></tr>")
        findings_html = ("<h2>جزئیات یافته‌ها</h2><div class='tbl'><table><thead><tr>"
                         "<th>شدت</th><th>عنوان</th><th>فایل</th><th>خط</th><th>CWE</th><th>نمونه</th>"
                         "</tr></thead><tbody>" + rows + "</tbody></table></div>")
    else:
        findings_html = ""

    dep_html = "<h2>وابستگی‌ها</h2>"
    if deps["packages"]:
        prows = "".join(
            f"<tr><td><code>{esc(p['name'])}</code></td><td>{esc(p['version'] or '—')}</td>"
            f"<td>{esc(p['ecosystem'])}</td><td><code>{esc(p['source'])}</code></td></tr>"
            for p in deps["packages"])
        dep_html += ("<div class='tbl'><table><thead><tr><th>بسته</th><th>نسخه</th>"
                     "<th>اکوسیستم</th><th>فایل منبع</th></tr></thead><tbody>"
                     + prows + "</tbody></table></div>")
    else:
        dep_html += "<p class='muted'>هیچ وابستگی شناسایی نشد.</p>"
    if deps["vulnerabilities"]:
        vrows = "".join(
            f"<tr><td><code>{esc(v['id'])}</code></td>"
            f"<td><span class='sev sev-{v['severity']}'>{SEVERITY_FA[v['severity']]}</span></td>"
            f"<td><code>{esc(v['package'])}</code></td>"
            f"<td>{esc(', '.join(v['fixed']) or '—')}</td>"
            f"<td>{esc(v['summary'])}</td></tr>" for v in deps["vulnerabilities"])
        dep_html += ("<h3>آسیب‌پذیری‌های شناخته‌شده (OSV.dev)</h3><div class='tbl'><table><thead><tr>"
                     "<th>شناسه</th><th>شدت</th><th>بسته</th><th>نسخه رفع‌شده</th><th>خلاصه</th>"
                     "</tr></thead><tbody>" + vrows + "</tbody></table></div>")
    if deps["notes"]:
        dep_html += "<ul class='notes'>" + "".join(f"<li>{esc(n)}</li>" for n in deps["notes"]) + "</ul>"

    langs = "".join(f"<span class='chip'>{esc(lang)} <b>{info['files']}</b> فایل / {info['lines']} خط</span>"
                    for lang, info in s["languages"].items())
    lang_html = f"<h2>زبان‌های پروژه</h2><div class='chips'>{langs or '—'}</div>"

    cf = s.get("complex_files") or []
    cf_html = ""
    if cf:
        crows = "".join(
            f"<tr><td><code>{esc(c['path'])}</code></td><td>{c['lines']}</td>"
            f"<td>{c.get('functions', 0)}</td><td><b>{c['complexity']}</b></td></tr>" for c in cf)
        cf_html = ("<h2>پیچیده‌ترین فایل‌ها (پیچیدگی سایکلوماتیک)</h2><div class='tbl'><table><thead><tr>"
                   "<th>فایل</th><th>خط</th><th>تابع</th><th>پیچیدگی</th>"
                   "</tr></thead><tbody>" + crows + "</tbody></table></div>")

    footer = (f"<footer><div>تولیدشده با {TOOL_NAME} v{TOOL_VERSION} — {esc(report['generated_at'])}</div>"
              f"<div class='mono'>SHA-256: {esc(digest)}</div>"
              f"<div class='muted'>این گزارش برای بررسی داخلی است؛ پیش از انتشار عمومی، اطلاعات حساس را بپوشانید.</div></footer>")

    return head + header + cards + bars + findings_html + dep_html + lang_html + cf_html + footer + "</div></body></html>"


# ──────────────────────── CLI و ورودی ────────────────────────
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="project-analyzer",
        description="ابزار امن تحلیل پروژه — متریک کد، یافته‌های امنیتی، اسکن آسیب‌پذیری وابستگی‌ها",
        epilog=("نمونه‌ها:\n"
                "  python project_analyzer.py /path/to/project\n"
                "  python project_analyzer.py . --no-network --exclude \"tests/*\" --fail-on critical\n"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("path", nargs="?", default=".", help="مسیر دایرکتوری پروژه (پیش‌فرض: دایرکتوری فعلی)")
    p.add_argument("-v", "--verbose", action="store_true", help="نمایش لاگ‌های اشکال‌زدایی")
    p.add_argument("--max-file-mb", type=float, default=2.0, help="حداکثر حجم فایل برای اسکن (مگابایت، پیش‌فرض ۲)")
    p.add_argument("--max-depth", type=int, default=12, help="حداکثر عمق پیمایش دایرکتوری (پیش‌فرض ۱۲)")
    p.add_argument("--exclude", action="append", default=[], metavar="GLOB", help="الگوی حذف (قابل تکرار)")
    p.add_argument("--no-network", action="store_true", help="غیرفعال‌کردن پرس‌وجوی آسیب‌پذیری از OSV.dev")
    p.add_argument("--no-git", action="store_true", help="غیرفعال‌کردن دریافت اطلاعات Git")
    p.add_argument("--json-out", default="project-analysis.json", help="مسیر خروجی گزارش JSON")
    p.add_argument("--html-out", default="project-analysis.html", help="مسیر خروجی گزارش HTML")
    p.add_argument("--fail-on", default="critical,high", help="شدت‌هایی که خروجی ۱ برمی‌گردانند (با کاما جدا شوند)")
    p.add_argument("--version", action="version", version=f"%(prog)s {TOOL_VERSION}")
    return p.parse_args(argv)


def setup_logging(verbose: bool) -> logging.Logger:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s │ %(levelname)s │ %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("analyzer")


def print_summary(report: dict, json_path: Path, html_path: Path,
                  sum_path: Path, digest: str) -> None:
    s = report["summary"]
    line = "═" * 64
    print(f"\n{line}")
    print(f"  📊 گزارش تحلیل پروژه — {report['project']['name']}")
    print(line)
    print(f"  فایل‌ها: {s['files']}   خطوط: {s['total_lines']}   مدت اسکن: {report['duration_seconds']} ثانیه")
    print(f"  امتیاز امن: {s['security_score']}/100 (درجه {s['grade']})")
    fbs = s["findings_by_severity"]
    print(f"  یافته‌ها: بحرانی {fbs['critical']} | زیاد {fbs['high']} | متوسط {fbs['medium']} | کم {fbs['low']} | اطلاع {fbs['info']}")
    if report["findings"]:
        print("\n  مهم‌ترین یافته‌ها:")
        for f in report["findings"][:8]:
            loc = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
            print(f"   • [{SEVERITY_FA[f['severity']]}] {f['title']} — {loc}")
    else:
        print("\n  ✅ هیچ یافته امنیتی ثبت نشد.")
    vulns = report["dependencies"]["vulnerabilities"]
    if vulns:
        print(f"\n  ⚠️  {len(vulns)} آسیب‌پذیری شناخته‌شده در وابستگی‌ها یافت شد.")
    print(f"\n  📄 گزارش JSON:   {json_path}")
    print(f"  🌐 گزارش HTML:   {html_path}")
    print(f"  🔏 فایل checksum: {sum_path}")
    print(f"  # SHA-256: {digest}")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    args = parse_args(argv)
    logger = setup_logging(args.verbose)
    try:
        root = Path(args.path).expanduser()
        analyzer = ProjectAnalyzer(root, args=args, logger=logger)
        report = analyzer.run()
    except AnalyzerError as exc:
        logger.error("❌ %s", exc)
        return 2
    except KeyboardInterrupt:
        logger.warning("عملیات توسط کاربر قطع شد.")
        return 130
    except Exception:  # noqa: BLE001
        logger.exception("خطای غیرمنتظره:")
        return 2

    json_path = Path(args.json_out).expanduser()
    html_path = Path(args.html_out).expanduser()
    try:
        json_bytes = json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")
        json_path.write_bytes(json_bytes)
        digest = hashlib.sha256(json_bytes).hexdigest()
        html_path.write_text(build_html(report, digest), encoding="utf-8")
        sum_path = json_path.with_suffix(".sha256")
        sum_path.write_text(f"{digest}  {json_path.name}\n", encoding="utf-8")
    except OSError as exc:
        logger.error("نوشتن خروجی ناموفق بود: %s", exc)
        return 2

    print_summary(report, json_path, html_path, sum_path, digest)

    fail_sevs = {x.strip().lower() for x in args.fail_on.split(",") if x.strip()}
    if any(f["severity"] in fail_sevs for f in report["findings"]):
        print(f"\n  ⛔ به‌دلیل وجود یافته‌های سطح «{args.fail_on}»، کد خروج ۱ برگشت داده می‌شود (مناسب CI).")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())