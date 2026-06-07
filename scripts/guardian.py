# -*- coding: utf-8 -*-
"""
🛡️ Econojin Guardian - Final Version
"""
import ast
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ═══════════════════════════════════════════════════════════
ROOT = Path(__file__).parent.resolve()
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# پوشه‌هایی که قطعاً نادیده گرفته شوند
IGNORE_DIRS = {
    ".venv",
    "venv",
    "env",
    "tutorial_env",
    "virtualenv",
    "node_modules",
    ".pnpm-store",
    "pnpm-global",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    ".next",
    ".nuxt",
    "artifacts",
    "cache",
    "typechain-types",
    ".cache",
    ".parcel-cache",
    "target",
    ".git",
    ".svn",
    ".idea",
    ".vscode",
    ".vs",
    "reports",
    "offline_packages",
    "data",
    "datasets",
    "uploads",
}

IGNORE_PATH_PARTS = [
    "site-packages",
    "guardian.py",
    "fix_security_findings.py",
    "Lib/site-packages",
    "_backup_",
    "_cleanup_",
]

MAX_FILES = 500


# ═══════════════════════════════════════════════════════════
class C:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


if sys.platform == "win32":
    os.system("")


def log(icon, msg, color=C.RESET):
    print(f"{color}{icon} {msg}{C.RESET}", flush=True)


def should_ignore(path: Path) -> bool:
    """آیا باید نادیده گرفته شود؟"""
    path_str = str(path).lower()

    # بررسی اجزای مسیر
    for part in path.parts:
        if part in IGNORE_DIRS:
            return True
        if part.startswith(".venv") or part.startswith("venv"):
            return True

    # بررسی پترن‌ها
    for pattern in IGNORE_PATH_PARTS:
        if pattern.lower() in path_str:
            return True

    return False


# ═══════════════════════════════════════════════════════════
SECRET_PATTERNS = [
    ("AWS Access Key", r"AKIA[0-9A-Z]{16}", "CRITICAL", 798),
    (
        "Copernicus Secret",
        r'(?i)(copernicus|cdse)[_\-]?(client[_\-]?secret|secret)\s*[=:]\s*[\'"][A-Za-z0-9_\-]{16,}[\'"]',
        "CRITICAL",
        798,
    ),
    (
        "Polygon Private Key",
        r'(?i)(polygon|matic|eth)[_\-]?(private[_\-]?key|pk)\s*[=:]\s*[\'"]?0x[A-Fa-f0-9]{64}[\'"]?',
        "CRITICAL",
        321,
    ),
    (
        "JWT Hardcoded Secret",
        r'(?i)(jwt|token)[_\-]?(secret|key)\s*[=:]\s*[\'"][A-Za-z0-9_\-!@#$%^&*]{12,}[\'"]',
        "HIGH",
        798,
    ),
    (
        "Database URL with creds",
        r'(postgresql|mysql|mongodb)://[^\'"\s]+:[^\'"\s]+@[^\s\'"]+',
        "HIGH",
        200,
    ),
    ("Generic Password", r'(?i)(password|passwd|pwd)\s*[=:]\s*[\'"][^\'"]{8,}[\'"]', "HIGH", 798),
    ("OpenAI Key", r"sk-[A-Za-z0-9]{32,}", "HIGH", 798),
    ("GitHub Token", r"ghp_[A-Za-z0-9]{36}", "HIGH", 798),
]

FALSE_POSITIVES = [
    "example",
    "placeholder",
    "your_",
    "xxx",
    "dummy",
    "test",
    "mock",
    "sk-test",
    "REPLACE_ME",
    "CHANGE_ME",
]


def scan_file(filepath: Path, findings: list):
    """اسکن یک فایل پایتون برای تمام مشکلات"""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return

    lines = content.split("\n")

    # ── 1. Syntax check ──
    try:
        compile(content, str(filepath), "exec")
    except SyntaxError as e:
        findings.append(
            {
                "title": "Syntax Error: " + str(e.msg),
                "severity": "CRITICAL",
                "category": "Syntax",
                "file": str(filepath),
                "line": e.lineno or 0,
                "evidence": str(e)[:200],
                "rec": "فایل را اصلاح کنید",
                "cwe": 670,
            }
        )
        return  # اگر syntax error دارد، بقیه اسکن‌ها ممکن است fail شوند

    # ── 2. Secrets ──
    for name, pattern, severity, cwe in SECRET_PATTERNS:
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("#"):
                continue
            if re.search(pattern, line):
                if any(marker in line.lower() for marker in FALSE_POSITIVES):
                    continue
                findings.append(
                    {
                        "title": "Hardcoded " + name,
                        "severity": severity,
                        "category": "Secrets",
                        "file": str(filepath),
                        "line": i,
                        "evidence": line.strip()[:150],
                        "rec": "از environment variable استفاده کنید",
                        "cwe": cwe,
                    }
                )

    # ── 3. AST-based scans ──
    try:
        tree = ast.parse(content)
    except Exception:
        return

    # Dangerous functions
    dangerous = {
        "eval": "CRITICAL",
        "exec": "CRITICAL",
        "os.system": "HIGH",
        "pickle.loads": "HIGH",
    }

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        fname = None
        if isinstance(node.func, ast.Name):
            fname = node.func.id
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                fname = node.func.value.id + "." + node.func.attr

        if not fname:
            continue

        severity = dangerous.get(fname)
        if severity:
            evidence = lines[node.lineno - 1].strip()[:150] if 0 < node.lineno <= len(lines) else ""
            findings.append(
                {
                    "title": "Dangerous: " + fname,
                    "severity": severity,
                    "category": "Dangerous Functions",
                    "file": str(filepath),
                    "line": node.lineno,
                    "evidence": evidence,
                    "rec": "استفاده از جایگزین امن",
                    "cwe": 95,
                }
            )

        # subprocess with shell=True
        if fname and fname.startswith("subprocess."):
            for kw in node.keywords:
                if (
                    kw.arg == "shell"
                    and isinstance(kw.value, ast.Constant)
                    and kw.value.value is True
                ):
                    evidence = (
                        lines[node.lineno - 1].strip()[:150]
                        if 0 < node.lineno <= len(lines)
                        else ""
                    )
                    findings.append(
                        {
                            "title": "subprocess with shell=True",
                            "severity": "CRITICAL",
                            "category": "Command Injection",
                            "file": str(filepath),
                            "line": node.lineno,
                            "evidence": evidence,
                            "rec": "استفاده از shell=False با لیست آرگومان‌ها",
                            "cwe": 78,
                        }
                    )

        # SQL injection
        if isinstance(node.func, ast.Attribute) and node.func.attr == "execute" and node.args:
            first = node.args[0]
            if isinstance(first, (ast.JoinedStr, ast.BinOp)):
                evidence = (
                    lines[node.lineno - 1].strip()[:150] if 0 < node.lineno <= len(lines) else ""
                )
                findings.append(
                    {
                        "title": "SQL Injection Risk",
                        "severity": "CRITICAL",
                        "category": "SQL Injection",
                        "file": str(filepath),
                        "line": node.lineno,
                        "evidence": evidence,
                        "rec": "استفاده از parameterized queries",
                        "cwe": 89,
                    }
                )

    # ── 4. Deprecations & crypto ──
    for i, line in enumerate(lines, 1):
        if "datetime.utcnow()" in line or "datetime.utcfromtimestamp" in line:
            findings.append(
                {
                    "title": "Deprecated datetime.utcnow()",
                    "severity": "MEDIUM",
                    "category": "Deprecation",
                    "file": str(filepath),
                    "line": i,
                    "evidence": line.strip()[:150],
                    "rec": "datetime.now(timezone.utc)",
                    "cwe": 477,
                }
            )

        if "hashlib.md5" in line or "hashlib.sha1" in line:
            findings.append(
                {
                    "title": "Weak Hash (MD5/SHA1)",
                    "severity": "MEDIUM",
                    "category": "Cryptography",
                    "file": str(filepath),
                    "line": i,
                    "evidence": line.strip()[:150],
                    "rec": "استفاده از SHA-256",
                    "cwe": 328,
                }
            )

        if re.search(r'algorithm\s*[=:]\s*[\'"]none[\'"]', line, re.IGNORECASE):
            findings.append(
                {
                    "title": "JWT algorithm='none'",
                    "severity": "CRITICAL",
                    "category": "JWT",
                    "file": str(filepath),
                    "line": i,
                    "evidence": line.strip()[:150],
                    "rec": "HS256 یا RS256",
                    "cwe": 327,
                }
            )

        if re.search(r"\brandom\.(random|randint|choice)\b", line):
            context = "\n".join(lines[max(0, i - 3) : min(len(lines), i + 2)])
            if any(w in context.lower() for w in ["password", "token", "secret", "key"]):
                findings.append(
                    {
                        "title": "Insecure Random in security context",
                        "severity": "HIGH",
                        "category": "Cryptography",
                        "file": str(filepath),
                        "line": i,
                        "evidence": line.strip()[:150],
                        "rec": "استفاده از secrets module",
                        "cwe": 330,
                    }
                )


def scan_solidity(filepath: Path, findings: list):
    """اسکن Smart Contracts"""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return

    for i, line in enumerate(content.split("\n"), 1):
        if "tx.origin" in line and ("require" in line or "if" in line):
            findings.append(
                {
                    "title": "tx.origin for auth",
                    "severity": "CRITICAL",
                    "category": "Smart Contract",
                    "file": str(filepath),
                    "line": i,
                    "evidence": line.strip()[:150],
                    "rec": "استفاده از msg.sender",
                    "cwe": 284,
                }
            )


def scan_dependencies(findings: list):
    """اسکن dependencies"""
    known = {
        "requests": ("2.31.0", "MEDIUM", "CVE-2023-32681"),
        "urllib3": ("2.0.6", "MEDIUM", "CVE-2023-43804"),
        "cryptography": ("41.0.0", "HIGH", "CVE-2023-38325"),
        "Pillow": ("10.0.1", "HIGH", "CVE-2023-44271"),
    }

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return

        packages = {p["name"].lower(): p["version"] for p in json.loads(result.stdout)}

        for pkg, (min_ver, sev, cve) in known.items():
            if pkg.lower() in packages:
                installed = packages[pkg.lower()]
                try:
                    t1 = tuple(map(int, installed.split(".")[:3]))
                    t2 = tuple(map(int, min_ver.split(".")[:3]))
                    if t1 < t2:
                        findings.append(
                            {
                                "title": "Vulnerable: " + pkg + "==" + installed,
                                "severity": sev,
                                "category": "Dependencies",
                                "file": "requirements.txt",
                                "line": 0,
                                "evidence": cve + " (need >= " + min_ver + ")",
                                "rec": "pip install --upgrade " + pkg,
                                "cwe": 1104,
                            }
                        )
                except Exception:
                    pass
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════
def escape_markdown(text):
    """Escape کاراکترهای خاص Markdown"""
    if not text:
        return ""
    return (
        text.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("*", "\\*")
        .replace("_", "\\_")
        .replace("{", "\\{")
        .replace("}", "\\}")
    )


def generate_report(findings: list, elapsed: float) -> Path:
    """تولید گزارش Markdown"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / ("guardian_" + timestamp + ".md")

    counts = defaultdict(int)
    for f in findings:
        counts[f["severity"]] += 1

    # Risk level
    if counts["CRITICAL"] > 0:
        risk = "🔴 CRITICAL"
    elif counts["HIGH"] > 0:
        risk = "🟠 HIGH"
    elif counts["MEDIUM"] > 0:
        risk = "🟡 MEDIUM"
    else:
        risk = "🟢 LOW"

    lines = []
    lines.append("# 🛡️ Guardian Report\n")
    lines.append("**Time:** " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    lines.append("**Project:** Econojin")
    lines.append("**Scan time:** " + str(round(elapsed, 1)) + "s\n")
    lines.append("## Risk: **" + risk + "**\n")
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    lines.append("| 🔴 CRITICAL | " + str(counts["CRITICAL"]) + " |")
    lines.append("| 🟠 HIGH | " + str(counts["HIGH"]) + " |")
    lines.append("| 🟡 MEDIUM | " + str(counts["MEDIUM"]) + " |")
    lines.append("| 🔵 LOW | " + str(counts["LOW"]) + " |")
    lines.append("| **Total** | **" + str(len(findings)) + "** |\n")
    lines.append("## Findings\n")

    if not findings:
        lines.append("🎉 هیچ مشکلی یافت نشد!\n")
    else:
        by_cat = defaultdict(list)
        for f in findings:
            by_cat[f["category"]].append(f)

        for cat, fs in sorted(by_cat.items()):
            lines.append("### 🏷️ " + cat + " (" + str(len(fs)) + ")\n")

            for f in fs:
                try:
                    rel = str(Path(f["file"]).relative_to(ROOT))
                except ValueError:
                    rel = f["file"]

                cwe_str = "CWE-" + str(f["cwe"]) if f.get("cwe") else "N/A"

                lines.append("#### " + f["title"])
                lines.append("")
                lines.append("- **Severity:** " + f["severity"])
                lines.append("- **Location:** `" + rel + "`:" + str(f["line"]))
                lines.append("- **CWE:** " + cwe_str)
                lines.append("")
                lines.append("**Evidence:**")
                lines.append("```")
                lines.append(escape_markdown(f["evidence"]))
                lines.append("```")
                lines.append("")
                lines.append("**Fix:** " + f["rec"])
                lines.append("")
                lines.append("---")
                lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


# ═══════════════════════════════════════════════════════════
def main():
    print(C.BOLD + C.CYAN)
    print("╔════════════════════════════════════════════╗")
    print("║  🛡️  ECONOJIN GUARDIAN - FINAL  🛡️        ║")
    print("╚════════════════════════════════════════════╝")
    print(C.RESET)
    print(C.GRAY + "Project: " + str(ROOT) + C.RESET)
    print(C.GRAY + "Time:    " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + C.RESET)
    print()

    start = time.time()
    findings = []

    # Discover files
    log("🔍", "جستجوی فایل‌های قابل اسکن...", C.CYAN)
    py_files = []
    sol_files = []
    skipped = 0

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if should_ignore(path):
            skipped += 1
            continue
        if path.suffix == ".py" and len(py_files) < MAX_FILES:
            py_files.append(path)
        elif path.suffix == ".sol" and len(sol_files) < MAX_FILES:
            sol_files.append(path)

    log(
        "✓",
        "یافت شد: "
        + str(len(py_files))
        + " Python + "
        + str(len(sol_files))
        + " Solidity (skipped: "
        + str(skipped)
        + ")",
        C.GREEN,
    )

    # Scan Python files
    log("🔒", "اسکن امنیتی " + str(len(py_files)) + " فایل...", C.CYAN)
    for i, py_file in enumerate(py_files, 1):
        if i % 20 == 0:
            log("...", "پیشرفت: " + str(i) + "/" + str(len(py_files)), C.GRAY)
        scan_file(py_file, findings)

    # Scan Solidity
    if sol_files:
        log("⛓️", "اسکن " + str(len(sol_files)) + " Solidity files...", C.CYAN)
        for sol_file in sol_files:
            scan_solidity(sol_file, findings)

    # Dependencies
    log("📦", "بررسی dependencies...", C.CYAN)
    scan_dependencies(findings)

    elapsed = time.time() - start

    # Generate report
    log("📊", "تولید گزارش...", C.CYAN)
    report_path = generate_report(findings, elapsed)

    # Summary
    counts = defaultdict(int)
    for f in findings:
        counts[f["severity"]] += 1

    print()
    print(C.BOLD + "═" * 60 + C.RESET)
    print(C.BOLD + "📊 SUMMARY (in " + str(round(elapsed, 1)) + "s)" + C.RESET)
    print(C.BOLD + "═" * 60 + C.RESET)
    print(C.RED + "  🔴 CRITICAL: " + str(counts["CRITICAL"]) + C.RESET)
    print(C.RED + "  🟠 HIGH:     " + str(counts["HIGH"]) + C.RESET)
    print(C.YELLOW + "  🟡 MEDIUM:   " + str(counts["MEDIUM"]) + C.RESET)
    print(C.BLUE + "  🔵 LOW:      " + str(counts["LOW"]) + C.RESET)
    print()
    print("  📄 Report: " + str(report_path.relative_to(ROOT)))

    if counts["CRITICAL"] > 0:
        print()
        print(C.RED + C.BOLD + "⚠️  CRITICAL findings detected!" + C.RESET)
        return 1
    elif counts["HIGH"] > 0:
        print()
        print(C.YELLOW + C.BOLD + "⚠️  HIGH findings detected" + C.RESET)
        return 2
    else:
        print()
        print(C.GREEN + C.BOLD + "✅ All checks passed!" + C.RESET)
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n" + C.YELLOW + "⚠️  Interrupted" + C.RESET)
        sys.exit(130)
    except Exception as e:
        print("\n" + C.RED + "❌ Error: " + str(e) + C.RESET)
        import traceback

        traceback.print_exc()
        sys.exit(99)
