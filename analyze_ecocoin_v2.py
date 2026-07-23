#!/usr/bin/env python3
"""
EcoCoin Professional Analyzer v2.0
===================================
تیم تحلیل:
  - متخصص امنیت بلاکچین (Blockchain Security Auditor)
  - معمار نرم‌افزار (Software Architect)
  - دانشمند داده (Data Scientist)
  - متخصص فرانت‌اند (Frontend Engineer)
  - متخصص تست (QA Engineer)
  - متخصص DevOps (DevOps Engineer)
  - متخصص i18n (Localization Engineer)
  - متخصص عملکرد (Performance Engineer)

خروجی: گزارش JSON + Markdown + امتیازدهی چندبُعدی
"""

import ast
import json
import re
import sys
import hashlib
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


# ═══════════════════════════════════════════════════════════
# ساختارهای داده
# ═══════════════════════════════════════════════════════════

@dataclass
class SecurityFinding:
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str
    file: str
    line: Optional[int]
    description: str
    recommendation: str
    cwe: Optional[str] = None  # CWE identifier


@dataclass
class ArchitectureIssue:
    category: str
    file: str
    description: str
    impact: str
    recommendation: str


@dataclass
class DataIntegrityIssue:
    category: str
    file: str
    description: str
    recommendation: str


@dataclass
class PerformanceIssue:
    category: str
    file: str
    description: str
    impact: str
    recommendation: str


@dataclass
class I18nIssue:
    category: str
    file: str
    description: str
    recommendation: str


@dataclass
class TestCoverageGap:
    category: str
    file: str
    description: str
    recommendation: str


@dataclass
class AnalysisReport:
    metadata: dict = field(default_factory=dict)
    scores: dict = field(default_factory=dict)
    security_findings: list = field(default_factory=list)
    architecture_issues: list = field(default_factory=list)
    data_integrity_issues: list = field(default_factory=list)
    performance_issues: list = field(default_factory=list)
    i18n_issues: list = field(default_factory=list)
    test_coverage_gaps: list = field(default_factory=list)
    contract_analysis: dict = field(default_factory=dict)
    api_analysis: dict = field(default_factory=dict)
    frontend_analysis: dict = field(default_factory=dict)
    dependency_analysis: dict = field(default_factory=dict)
    summary: dict = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════
# ۱. متخصص امنیت بلاکچین
# ═══════════════════════════════════════════════════════════

class BlockchainSecurityAuditor:
    """تحلیل امنیتی قراردادهای هوشمند"""

    CRITICAL_PATTERNS = [
        (r'\bselfdestruct\b', "CWE-672", "استفاده از selfdestruct — خطر نابودی قرارداد"),
        (r'\bdelegatecall\b', "CWE-829", "استفاده از delegatecall — خطر اجرای کد مخرب"),
        (r'\btx\.origin\b', "CWE-477", "استفاده از tx.origin — آسیب‌پذیر به فیشینگ"),
        (r'\bblock\.timestamp\b.*[<>]=?\s*\d+', "CWE-330", "وابستگی به timestamp — قابل دستکاری توسط ماینر"),
        (r'\bblock\.number\b.*[<>]=?\s*\d+', "CWE-330", "وابستگی به block.number — قابل پیش‌بینی"),
    ]

    HIGH_PATTERNS = [
        (r'function\s+\w+\s*\([^)]*\)\s*public\s*(?!.*\bonly\w+\b)', "CWE-862", "تابع public بدون access control"),
        (r'\btransfer\s*\(', "CWE-841", "استفاده از transfer — محدودیت ۲۳۰۰ gas"),
        (r'\bcall\s*\{\s*value\s*:', "CWE-841", "استفاده از call با value — خطر reentrancy"),
        (r'\bapprove\s*\(', "CWE-362", "استفاده از approve — خطر race condition"),
    ]

    MEDIUM_PATTERNS = [
        (r'\brequire\s*\([^)]*\)\s*;', "CWE-754", "require بدون پیام خطا — دشواری دیباگ"),
        (r'\bpragma\s+solidity\s*\^?0\.[0-7]\.', "CWE-1104", "نسخهٔ قدیمی Solidity"),
        (r'\bnow\b', "CWE-330", "استفاده از now — منسوخ‌شده"),
        (r'\bmsg\.sender\b.*==.*\bmsg\.sender\b', "CWE-571", "مقایسهٔ تکراری msg.sender"),
    ]

    LOW_PATTERNS = [
        (r'\buint\s+\w+\s*=\s*0\s*;', "CWE-563", "مقداردهی اولیهٔ غیرضروری"),
        (r'\bpublic\s+\w+\s*\[\s*\]', "CWE-1061", "آرایهٔ public — مصرف gas بالا"),
    ]

    REQUIRED_SECURITY_PATTERNS = [
        (r'\bReentrancyGuard\b', "محافظ Reentrancy"),
        (r'\bnonReentrant\b', "استفاده از nonReentrant"),
        (r'\bonlyOwner\b|\bonlySteward\b|\bonlyAdmin\b', "Access Control"),
        (r'\brequire\s*\(', "Input Validation"),
        (r'\bemit\s+\w+\(', "Event Logging"),
        (r'\bSafeMath\b|\bchecked\s*\{', "Safe Arithmetic"),
    ]

    def __init__(self):
        self.findings: list[SecurityFinding] = []

    def analyze_contract(self, file_path: Path, content: str) -> dict:
        """تحلیل کامل یک قرارداد هوشمند"""
        lines = content.split('\n')
        contract_info = {
            "file": str(file_path),
            "name": self._extract_contract_name(content),
            "functions": [],
            "events": [],
            "modifiers": [],
            "state_variables": [],
            "inheritance": [],
            "security_score": 0,
            "findings": [],
        }

        # استخراج اطلاعات قرارداد
        contract_info["functions"] = self._extract_functions(content)
        contract_info["events"] = self._extract_events(content)
        contract_info["modifiers"] = self._extract_modifiers(content)
        contract_info["state_variables"] = self._extract_state_variables(content)
        contract_info["inheritance"] = self._extract_inheritance(content)

        # بررسی الگوهای بحرانی
        for pattern, cwe, desc in self.CRITICAL_PATTERNS:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    self.findings.append(SecurityFinding(
                        severity="CRITICAL",
                        category="Smart Contract",
                        file=str(file_path),
                        line=i,
                        description=desc,
                        recommendation=self._get_recommendation(cwe),
                        cwe=cwe,
                    ))
                    contract_info["findings"].append(("CRITICAL", desc, i))

        # بررسی الگوهای پرخطر
        for pattern, cwe, desc in self.HIGH_PATTERNS:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    self.findings.append(SecurityFinding(
                        severity="HIGH",
                        category="Smart Contract",
                        file=str(file_path),
                        line=i,
                        description=desc,
                        recommendation=self._get_recommendation(cwe),
                        cwe=cwe,
                    ))
                    contract_info["findings"].append(("HIGH", desc, i))

        # بررسی الگوهای متوسط
        for pattern, cwe, desc in self.MEDIUM_PATTERNS:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    self.findings.append(SecurityFinding(
                        severity="MEDIUM",
                        category="Smart Contract",
                        file=str(file_path),
                        line=i,
                        description=desc,
                        recommendation=self._get_recommendation(cwe),
                        cwe=cwe,
                    ))
                    contract_info["findings"].append(("MEDIUM", desc, i))

        # بررسی الگوهای کم‌خطر
        for pattern, cwe, desc in self.LOW_PATTERNS:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    self.findings.append(SecurityFinding(
                        severity="LOW",
                        category="Smart Contract",
                        file=str(file_path),
                        line=i,
                        description=desc,
                        recommendation=self._get_recommendation(cwe),
                        cwe=cwe,
                    ))
                    contract_info["findings"].append(("LOW", desc, i))

        # بررسی الگوهای امنیتی مورد نیاز
        missing_patterns = []
        for pattern, name in self.REQUIRED_SECURITY_PATTERNS:
            if not re.search(pattern, content):
                missing_patterns.append(name)
                self.findings.append(SecurityFinding(
                    severity="HIGH",
                    category="Smart Contract",
                    file=str(file_path),
                    line=None,
                    description=f"فقدان {name}",
                    recommendation=f"افزودن {name} به قرارداد",
                ))

        contract_info["missing_security_patterns"] = missing_patterns

        # محاسبهٔ امتیاز امنیتی
        critical_count = sum(1 for f in contract_info["findings"] if f[0] == "CRITICAL")
        high_count = sum(1 for f in contract_info["findings"] if f[0] == "HIGH")
        medium_count = sum(1 for f in contract_info["findings"] if f[0] == "MEDIUM")
        low_count = sum(1 for f in contract_info["findings"] if f[0] == "LOW")

        score = 100
        score -= critical_count * 30
        score -= high_count * 15
        score -= medium_count * 5
        score -= low_count * 2
        score -= len(missing_patterns) * 10
        contract_info["security_score"] = max(0, score)

        return contract_info

    def _extract_contract_name(self, content: str) -> str:
        match = re.search(r'contract\s+(\w+)', content)
        return match.group(1) if match else "Unknown"

    def _extract_functions(self, content: str) -> list:
        functions = []
        pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*([\w\s]*)'
        for match in re.finditer(pattern, content):
            name, params, modifiers = match.groups()
            visibility = "public"
            mutability = "nonpayable"
            if "external" in modifiers: visibility = "external"
            elif "internal" in modifiers: visibility = "internal"
            elif "private" in modifiers: visibility = "private"
            if "view" in modifiers: mutability = "view"
            elif "pure" in modifiers: mutability = "pure"
            elif "payable" in modifiers: mutability = "payable"
            functions.append({
                "name": name,
                "params": params.strip(),
                "visibility": visibility,
                "mutability": mutability,
            })
        return functions

    def _extract_events(self, content: str) -> list:
        events = []
        pattern = r'event\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(pattern, content):
            name, params = match.groups()
            events.append({"name": name, "params": params.strip()})
        return events

    def _extract_modifiers(self, content: str) -> list:
        modifiers = []
        pattern = r'modifier\s+(\w+)'
        for match in re.finditer(pattern, content):
            modifiers.append(match.group(1))
        return modifiers

    def _extract_state_variables(self, content: str) -> list:
        variables = []
        pattern = r'(mapping\s*\([^)]+\)|\w+)\s+(public|private|internal)?\s*(\w+)\s*;'
        for match in re.finditer(pattern, content):
            var_type, visibility, name = match.groups()
            variables.append({
                "type": var_type.strip(),
                "visibility": visibility or "internal",
                "name": name,
            })
        return variables

    def _extract_inheritance(self, content: str) -> list:
        match = re.search(r'contract\s+\w+\s+is\s+([\w\s,]+)\s*\{', content)
        if match:
            return [x.strip() for x in match.group(1).split(',')]
        return []

    def _get_recommendation(self, cwe: str) -> str:
        recommendations = {
            "CWE-672": "از selfdestruct استفاده نکنید؛ از Pausable استفاده کنید",
            "CWE-829": "از delegatecall اجتناب کنید یا از proxy pattern امن استفاده کنید",
            "CWE-477": "به‌جای tx.origin از msg.sender استفاده کنید",
            "CWE-330": "از oracle برای زمان استفاده کنید نه block.timestamp",
            "CWE-862": "modifier دسترسی (onlyOwner/onlySteward) اضافه کنید",
            "CWE-841": "از call با checks-effects-interactions استفاده کنید",
            "CWE-362": "از increaseAllowance/decreaseAllowance استفاده کنید",
            "CWE-754": "پیام خطا به require اضافه کنید",
            "CWE-1104": "به Solidity ^0.8.20 ارتقا دهید",
            "CWE-563": "مقداردهی اولیهٔ غیرضروری را حذف کنید",
            "CWE-1061": "از getter function به‌جای آرایهٔ public استفاده کنید",
        }
        return recommendations.get(cwe, "بررسی و رفع مشکل")


# ═══════════════════════════════════════════════════════════
# ۲. معمار نرم‌افزار
# ═══════════════════════════════════════════════════════════

class SoftwareArchitect:
    """تحلیل معماری نرم‌افزار"""

    def __init__(self):
        self.issues: list[ArchitectureIssue] = []

    def analyze_api_structure(self, api_files: list[Path]) -> dict:
        """تحلیل ساختار API"""
        analysis = {
            "total_endpoints": 0,
            "endpoints_by_method": defaultdict(int),
            "endpoints_by_module": defaultdict(int),
            "missing_auth_endpoints": [],
            "missing_validation": [],
            "inconsistent_naming": [],
        }

        for file_path in api_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                module_name = file_path.stem

                # استخراج endpointها
                endpoint_pattern = r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
                for match in re.finditer(endpoint_pattern, content):
                    method, path = match.groups()
                    analysis["endpoints_by_method"][method.upper()] += 1
                    analysis["endpoints_by_module"][module_name] += 1
                    analysis["total_endpoints"] += 1

                    # بررسی auth
                    if method.upper() in ["POST", "PUT", "DELETE", "PATCH"]:
                        if "Depends(get_current_user)" not in content and "Depends(get_current_active_user)" not in content:
                            analysis["missing_auth_endpoints"].append(f"{method.upper()} {path} in {module_name}")
                            self.issues.append(ArchitectureIssue(
                                category="API Security",
                                file=str(file_path),
                                description=f"Endpoint {method.upper()} {path} بدون احراز هویت",
                                impact="دسترسی غیرمجاز به عملیات حساس",
                                recommendation="افزودن Depends(get_current_user)",
                            ))

                # بررسی validation
                if "BaseModel" in content:
                    if "validator" not in content and "field_validator" not in content:
                        analysis["missing_validation"].append(module_name)

            except Exception as e:
                self.issues.append(ArchitectureIssue(
                    category="File Error",
                    file=str(file_path),
                    description=f"خطا در خواندن فایل: {e}",
                    impact="عدم امکان تحلیل",
                    recommendation="بررسی فایل",
                ))

        return analysis

    def analyze_dependency_injection(self, content: str, file_path: Path) -> list:
        """تحلیل dependency injection"""
        issues = []
        if "Depends(" not in content and "router" in content:
            issues.append(ArchitectureIssue(
                category="Dependency Injection",
                file=str(file_path),
                description="عدم استفاده از dependency injection",
                impact="تست‌پذیری پایین و coupling بالا",
                recommendation="استفاده از Depends() برای تزریق وابستگی‌ها",
            ))
        return issues


# ═══════════════════════════════════════════════════════════
# ۳. دانشمند داده
# ═══════════════════════════════════════════════════════════

class DataScientist:
    """تحلیل یکپارچگی داده‌ها"""

    def __init__(self):
        self.issues: list[DataIntegrityIssue] = []

    def analyze_data_models(self, model_files: list[Path]) -> dict:
        """تحلیل مدل‌های داده"""
        analysis = {
            "total_models": 0,
            "models_by_module": defaultdict(int),
            "missing_indexes": [],
            "missing_relationships": [],
            "inconsistent_types": [],
        }

        for file_path in model_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                module_name = file_path.stem

                # استخراج کلاس‌های مدل
                class_pattern = r'class\s+(\w+)\s*\(([^)]*)\)'
                for match in re.finditer(class_pattern, content):
                    class_name, bases = match.groups()
                    if "Base" in bases or "Model" in bases:
                        analysis["total_models"] += 1
                        analysis["models_by_module"][module_name] += 1

                # بررسی index
                if "Column(" in content and "index=True" not in content:
                    analysis["missing_indexes"].append(module_name)
                    self.issues.append(DataIntegrityIssue(
                        category="Database Index",
                        file=str(file_path),
                        description="فقدان index روی ستون‌های پرکاربرد",
                        recommendation="افزودن index=True روی ستون‌های کلیدی",
                    ))

                # بررسی relationship
                if "ForeignKey" in content and "relationship" not in content:
                    analysis["missing_relationships"].append(module_name)

            except Exception as e:
                self.issues.append(DataIntegrityIssue(
                    category="File Error",
                    file=str(file_path),
                    description=f"خطا در خواندن فایل: {e}",
                    recommendation="بررسی فایل",
                ))

        return analysis


# ═══════════════════════════════════════════════════════════
# ۴. متخصص فرانت‌اند
# ═══════════════════════════════════════════════════════════

class FrontendEngineer:
    """تحلیل کامپوننت‌های فرانت‌اند"""

    def __init__(self):
        self.issues: list[ArchitectureIssue] = []

    def analyze_components(self, component_files: list[Path]) -> dict:
        """تحلیل کامپوننت‌ها"""
        analysis = {
            "total_components": 0,
            "components_by_type": defaultdict(int),
            "missing_error_boundaries": [],
            "missing_loading_states": [],
            "missing_key_props": [],
            "large_components": [],
        }

        for file_path in component_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.split('\n')

                # شمارش کامپوننت‌ها
                component_pattern = r'(?:export\s+)?(?:default\s+)?function\s+(\w+)|(?:export\s+)?const\s+(\w+)\s*=\s*(?:\([^)]*\)|)\s*=>'
                for match in re.finditer(component_pattern, content):
                    name = match.group(1) or match.group(2)
                    if name and name[0].isupper():
                        analysis["total_components"] += 1
                        analysis["components_by_type"]["function"] += 1

                # بررسی error boundary
                if "ErrorBoundary" not in content and len(lines) > 100:
                    analysis["missing_error_boundaries"].append(str(file_path))

                # بررسی loading state
                if "isLoading" not in content and "loading" not in content and "useQuery" in content:
                    analysis["missing_loading_states"].append(str(file_path))

                # بررسی key prop
                if ".map(" in content and "key=" not in content:
                    analysis["missing_key_props"].append(str(file_path))
                    self.issues.append(ArchitectureIssue(
                        category="React Best Practice",
                        file=str(file_path),
                        description="فقدان key prop در لیست‌ها",
                        impact="مشکل در رندر مجدد و عملکرد",
                        recommendation="افزودن key prop منحصربه‌فرد",
                    ))

                # بررسی کامپوننت‌های بزرگ
                if len(lines) > 300:
                    analysis["large_components"].append({
                        "file": str(file_path),
                        "lines": len(lines),
                    })
                    self.issues.append(ArchitectureIssue(
                        category="Component Size",
                        file=str(file_path),
                        description=f"کامپوننت بزرگ ({len(lines)} خط)",
                        impact="نگهداری دشوار و تست‌پذیری پایین",
                        recommendation="تقسیم به کامپوننت‌های کوچک‌تر",
                    ))

            except Exception as e:
                self.issues.append(ArchitectureIssue(
                    category="File Error",
                    file=str(file_path),
                    description=f"خطا در خواندن فایل: {e}",
                    impact="عدم امکان تحلیل",
                    recommendation="بررسی فایل",
                ))

        return analysis


# ═══════════════════════════════════════════════════════════
# ۵. متخصص تست
# ═══════════════════════════════════════════════════════════

class QAEngineer:
    """تحلیل پوشش تست"""

    def __init__(self):
        self.gaps: list[TestCoverageGap] = []

    def analyze_test_coverage(self, test_files: list[Path], source_files: list[Path]) -> dict:
        """تحلیل پوشش تست"""
        analysis = {
            "total_test_files": len(test_files),
            "total_source_files": len(source_files),
            "coverage_ratio": 0,
            "untested_modules": [],
            "test_patterns": defaultdict(int),
        }

        # استخراج نام ماژول‌های تست‌شده
        tested_modules = set()
        for test_file in test_files:
            name = test_file.stem.replace("test_", "").replace("_test", "")
            tested_modules.add(name)

            # استخراج الگوهای تست
            try:
                content = test_file.read_text(encoding="utf-8")
                if "pytest" in content: analysis["test_patterns"]["pytest"] += 1
                if "unittest" in content: analysis["test_patterns"]["unittest"] += 1
                if "jest" in content: analysis["test_patterns"]["jest"] += 1
                if "vitest" in content: analysis["test_patterns"]["vitest"] += 1
            except:
                pass

        # یافتن ماژول‌های بدون تست
        for source_file in source_files:
            name = source_file.stem
            if name not in tested_modules and name not in ["__init__", "conftest"]:
                analysis["untested_modules"].append(str(source_file))
                self.gaps.append(TestCoverageGap(
                    category="Missing Tests",
                    file=str(source_file),
                    description=f"ماژول {name} بدون تست",
                    recommendation=f"افزودن تست برای {name}",
                ))

        if len(source_files) > 0:
            analysis["coverage_ratio"] = len(tested_modules) / len(source_files)

        return analysis


# ═══════════════════════════════════════════════════════════
# ۶. متخصص DevOps
# ═══════════════════════════════════════════════════════════

class DevOpsEngineer:
    """تحلیل زیرساخت و استقرار"""

    def __init__(self):
        self.issues: list[ArchitectureIssue] = []

    def analyze_infrastructure(self, root: Path) -> dict:
        """تحلیل زیرساخت"""
        analysis = {
            "has_dockerfile": False,
            "has_docker_compose": False,
            "has_ci_cd": False,
            "has_env_example": False,
            "has_health_check": False,
            "missing_configs": [],
        }

        # بررسی Dockerfile
        if (root / "Dockerfile").exists():
            analysis["has_dockerfile"] = True
        else:
            analysis["missing_configs"].append("Dockerfile")

        # بررسی docker-compose
        if (root / "docker-compose.yml").exists() or (root / "docker-compose.yaml").exists():
            analysis["has_docker_compose"] = True
        else:
            analysis["missing_configs"].append("docker-compose.yml")

        # بررسی CI/CD
        github_workflows = root / ".github" / "workflows"
        if github_workflows.exists():
            analysis["has_ci_cd"] = True
        else:
            analysis["missing_configs"].append(".github/workflows")

        # بررسی env example
        if (root / ".env.example").exists():
            analysis["has_env_example"] = True
        else:
            analysis["missing_configs"].append(".env.example")

        return analysis


# ═══════════════════════════════════════════════════════════
# ۷. متخصص i18n
# ═══════════════════════════════════════════════════════════

class LocalizationEngineer:
    """تحلیل بین‌المللی‌سازی"""

    def __init__(self):
        self.issues: list[I18nIssue] = []

    def analyze_i18n(self, i18n_files: list[Path]) -> dict:
        """تحلیل i18n"""
        analysis = {
            "total_i18n_files": len(i18n_files),
            "languages": set(),
            "missing_translations": [],
            "inconsistent_keys": [],
        }

        for file_path in i18n_files:
            try:
                content = file_path.read_text(encoding="utf-8")

                # استخراج زبان‌ها
                lang_match = re.search(r'["\'](\w{2})["\']', file_path.name)
                if lang_match:
                    analysis["languages"].add(lang_match.group(1))

                # بررسی کلیدها
                if file_path.suffix == ".json":
                    data = json.loads(content)
                    # بررسی کلیدهای خالی
                    for key, value in self._flatten_dict(data).items():
                        if not value or value.strip() == "":
                            analysis["missing_translations"].append(f"{file_path.name}: {key}")
                            self.issues.append(I18nIssue(
                                category="Missing Translation",
                                file=str(file_path),
                                description=f"کلید {key} خالی است",
                                recommendation="افزودن ترجمه",
                            ))

            except Exception as e:
                self.issues.append(I18nIssue(
                    category="File Error",
                    file=str(file_path),
                    description=f"خطا در خواندن فایل: {e}",
                    recommendation="بررسی فایل",
                ))

        analysis["languages"] = list(analysis["languages"])
        return analysis

    def _flatten_dict(self, d: dict, parent_key: str = "") -> dict:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key).items())
            else:
                items.append((new_key, v))
        return dict(items)


# ═══════════════════════════════════════════════════════════
# ۸. متخصص عملکرد
# ═══════════════════════════════════════════════════════════

class PerformanceEngineer:
    """تحلیل عملکرد"""

    def __init__(self):
        self.issues: list[PerformanceIssue] = []

    def analyze_performance(self, source_files: list[Path]) -> dict:
        """تحلیل عملکرد"""
        analysis = {
            "large_files": [],
            "potential_n_plus_one": [],
            "missing_caching": [],
            "synchronous_operations": [],
        }

        for file_path in source_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.split('\n')

                # بررسی فایل‌های بزرگ
                if len(lines) > 500:
                    analysis["large_files"].append({
                        "file": str(file_path),
                        "lines": len(lines),
                    })
                    self.issues.append(PerformanceIssue(
                        category="File Size",
                        file=str(file_path),
                        description=f"فایل بزرگ ({len(lines)} خط)",
                        impact="زمان بارگذاری بالا",
                        recommendation="تقسیم فایل",
                    ))

                # بررسی N+1 query
                if "for " in content and "query" in content.lower():
                    if "join" not in content.lower() and "in_" not in content:
                        analysis["potential_n_plus_one"].append(str(file_path))
                        self.issues.append(PerformanceIssue(
                            category="N+1 Query",
                            file=str(file_path),
                            description="احتمال N+1 query",
                            impact="کندی در بازیابی داده",
                            recommendation="استفاده از join یا eager loading",
                        ))

                # بررسی عملیات همگام
                if "time.sleep" in content:
                    analysis["synchronous_operations"].append(str(file_path))
                    self.issues.append(PerformanceIssue(
                        category="Blocking Operation",
                        file=str(file_path),
                        description="استفاده از time.sleep — مسدودسازی event loop",
                        impact="کندی سرور",
                        recommendation="استفاده از asyncio.sleep",
                    ))

            except Exception:
                pass

        return analysis


# ═══════════════════════════════════════════════════════════
# تحلیل‌گر اصلی
# ═══════════════════════════════════════════════════════════

class EcoCoinAnalyzer:
    """تحلیل‌گر اصلی — هماهنگ‌کنندهٔ تیم"""

    IGNORE_DIRS = {
        "node_modules", ".git", "__pycache__", ".venv", "venv",
        ".next", "dist", "build", ".turbo", "coverage",
        ".pytest_cache", ".mypy_cache", ".ruff_cache", ".pnpm-store",
    }

    def __init__(self, root: Path):
        self.root = root
        self.report = AnalysisReport()
        self.report.metadata = {
            "scan_time": datetime.now().isoformat(),
            "project_root": str(root),
            "analyzer_version": "2.0.0",
            "team": [
                "Blockchain Security Auditor",
                "Software Architect",
                "Data Scientist",
                "Frontend Engineer",
                "QA Engineer",
                "DevOps Engineer",
                "Localization Engineer",
                "Performance Engineer",
            ],
        }

        #初始化 تحلیل‌گران
        self.security_auditor = BlockchainSecurityAuditor()
        self.architect = SoftwareArchitect()
        self.data_scientist = DataScientist()
        self.frontend_engineer = FrontendEngineer()
        self.qa_engineer = QAEngineer()
        self.devops_engineer = DevOpsEngineer()
        self.localization_engineer = LocalizationEngineer()
        self.performance_engineer = PerformanceEngineer()

    def run_full_analysis(self) -> AnalysisReport:
        """اجرای تحلیل کامل"""
        print("=" * 70)
        print("  EcoCoin Professional Analyzer v2.0")
        print("  تیم تحلیل: ۸ متخصص")
        print("=" * 70)

        # ۱. تحلیل قراردادهای هوشمند
        print("\n[۱/۸] تحلیل قراردادهای هوشمند...")
        contract_files = list(self.root.rglob("*.sol"))
        contract_files = [f for f in contract_files if not any(d in str(f) for d in self.IGNORE_DIRS)]
        contracts = []
        for cf in contract_files:
            try:
                content = cf.read_text(encoding="utf-8")
                contracts.append(self.security_auditor.analyze_contract(cf, content))
            except Exception as e:
                print(f"    ⚠ خطا در {cf}: {e}")
        self.report.contract_analysis = {
            "total_contracts": len(contracts),
            "contracts": contracts,
            "avg_security_score": sum(c["security_score"] for c in contracts) / len(contracts) if contracts else 0,
        }
        print(f"    ✓ {len(contracts)} قرارداد تحلیل شد")

        # ۲. تحلیل API
        print("\n[۲/۸] تحلیل API...")
        api_files = list(self.root.rglob("*.py"))
        api_files = [f for f in api_files if "routes" in str(f) or "router" in str(f)]
        api_files = [f for f in api_files if not any(d in str(f) for d in self.IGNORE_DIRS)]
        self.report.api_analysis = self.architect.analyze_api_structure(api_files)
        print(f"    ✓ {self.report.api_analysis['total_endpoints']} endpoint تحلیل شد")

        # ۳. تحلیل مدل‌های داده
        print("\n[۳/۸] تحلیل مدل‌های داده...")
        model_files = list(self.root.rglob("*.py"))
        model_files = [f for f in model_files if "models" in str(f) or "schemas" in str(f)]
        model_files = [f for f in model_files if not any(d in str(f) for d in self.IGNORE_DIRS)]
        self.report.data_integrity_issues = self.data_scientist.issues
        self.report.api_analysis["data_models"] = self.data_scientist.analyze_data_models(model_files)
        print(f"    ✓ {self.report.api_analysis['data_models']['total_models']} مدل تحلیل شد")

        # ۴. تحلیل فرانت‌اند
        print("\n[۴/۸] تحلیل فرانت‌اند...")
        component_files = list(self.root.rglob("*.tsx")) + list(self.root.rglob("*.jsx"))
        component_files = [f for f in component_files if not any(d in str(f) for d in self.IGNORE_DIRS)]
        self.report.frontend_analysis = self.frontend_engineer.analyze_components(component_files)
        print(f"    ✓ {self.report.frontend_analysis['total_components']} کامپوننت تحلیل شد")

        # ۵. تحلیل تست
        print("\n[۵/۸] تحلیل پوشش تست...")
        test_files = list(self.root.rglob("test_*.py")) + list(self.root.rglob("*_test.py"))
        test_files += list(self.root.rglob("*.test.ts")) + list(self.root.rglob("*.test.tsx"))
        test_files = [f for f in test_files if not any(d in str(f) for d in self.IGNORE_DIRS)]
        source_files = list(self.root.rglob("*.py")) + list(self.root.rglob("*.ts")) + list(self.root.rglob("*.tsx"))
        source_files = [f for f in source_files if not any(d in str(f) for d in self.IGNORE_DIRS)]
        source_files = [f for f in source_files if "test" not in str(f).lower()]
        self.report.test_coverage_gaps = self.qa_engineer.gaps
        self.report.api_analysis["test_coverage"] = self.qa_engineer.analyze_test_coverage(test_files, source_files)
        print(f"    ✓ {len(test_files)} فایل تست تحلیل شد")

        # ۶. تحلیل DevOps
        print("\n[۶/۸] تحلیل DevOps...")
        self.report.architecture_issues = self.devops_engineer.issues
        self.report.api_analysis["infrastructure"] = self.devops_engineer.analyze_infrastructure(self.root)
        print("    ✓ زیرساخت تحلیل شد")

        # ۷. تحلیل i18n
        print("\n[۷/۸] تحلیل i18n...")
        i18n_files = list(self.root.rglob("*.json"))
        i18n_files = [f for f in i18n_files if "locales" in str(f) or "i18n" in str(f)]
        i18n_files = [f for f in i18n_files if not any(d in str(f) for d in self.IGNORE_DIRS)]
        self.report.i18n_issues = self.localization_engineer.issues
        self.report.api_analysis["i18n"] = self.localization_engineer.analyze_i18n(i18n_files)
        print(f"    ✓ {len(i18n_files)} فایل i18n تحلیل شد")

        # ۸. تحلیل عملکرد
        print("\n[۸/۸] تحلیل عملکرد...")
        self.report.performance_issues = self.performance_engineer.issues
        self.report.api_analysis["performance"] = self.performance_engineer.analyze_performance(source_files)
        print("    ✓ عملکرد تحلیل شد")

        # محاسبهٔ امتیازات
        self._calculate_scores()

        # خلاصه
        self._generate_summary()

        return self.report

    def _calculate_scores(self):
        """محاسبهٔ امتیازات چندبُعدی"""
        # امتیاز امنیت
        critical = sum(1 for f in self.security_auditor.findings if f.severity == "CRITICAL")
        high = sum(1 for f in self.security_auditor.findings if f.severity == "HIGH")
        medium = sum(1 for f in self.security_auditor.findings if f.severity == "MEDIUM")
        security_score = max(0, 100 - critical * 30 - high * 15 - medium * 5)

        # امتیاز معماری
        arch_issues = len(self.architect.issues)
        arch_score = max(0, 100 - arch_issues * 10)

        # امتیاز داده
        data_issues = len(self.data_scientist.issues)
        data_score = max(0, 100 - data_issues * 10)

        # امتیاز فرانت‌اند
        fe_issues = len(self.frontend_engineer.issues)
        fe_score = max(0, 100 - fe_issues * 5)

        # امتیاز تست
        test_ratio = self.report.api_analysis.get("test_coverage", {}).get("coverage_ratio", 0)
        test_score = int(test_ratio * 100)

        # امتیاز DevOps
        infra = self.report.api_analysis.get("infrastructure", {})
        devops_score = sum([
            infra.get("has_dockerfile", False),
            infra.get("has_docker_compose", False),
            infra.get("has_ci_cd", False),
            infra.get("has_env_example", False),
        ]) * 25

        # امتیاز i18n
        i18n_issues = len(self.localization_engineer.issues)
        i18n_score = max(0, 100 - i18n_issues * 5)

        # امتیاز عملکرد
        perf_issues = len(self.performance_engineer.issues)
        perf_score = max(0, 100 - perf_issues * 5)

        self.report.scores = {
            "security": security_score,
            "architecture": arch_score,
            "data_integrity": data_score,
            "frontend": fe_score,
            "test_coverage": test_score,
            "devops": devops_score,
            "i18n": i18n_score,
            "performance": perf_score,
            "overall": int((security_score + arch_score + data_score + fe_score +
                           test_score + devops_score + i18n_score + perf_score) / 8),
        }

    def _generate_summary(self):
        """تولید خلاصه"""
        self.report.summary = {
            "total_files_analyzed": sum([
                self.report.contract_analysis.get("total_contracts", 0),
                self.report.api_analysis.get("total_endpoints", 0),
                self.report.frontend_analysis.get("total_components", 0),
            ]),
            "total_security_findings": len(self.security_auditor.findings),
            "critical_findings": sum(1 for f in self.security_auditor.findings if f.severity == "CRITICAL"),
            "high_findings": sum(1 for f in self.security_auditor.findings if f.severity == "HIGH"),
            "total_architecture_issues": len(self.architect.issues),
            "total_data_issues": len(self.data_scientist.issues),
            "total_performance_issues": len(self.performance_engineer.issues),
            "total_i18n_issues": len(self.localization_engineer.issues),
            "total_test_gaps": len(self.qa_engineer.gaps),
        }

    def save_reports(self, output_dir: Path):
        """ذخیرهٔ گزارش‌ها"""
        output_dir.mkdir(parents=True, exist_ok=True)

        # گزارش JSON
        json_path = output_dir / "ecocoin_analysis_v2.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(asdict(self.report), f, ensure_ascii=False, indent=2, default=str)

        # گزارش Markdown
        md_path = output_dir / "ecocoin_analysis_v2.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self._generate_markdown())

        return json_path, md_path

    def _generate_markdown(self) -> str:
        """تولید گزارش Markdown"""
        lines = []
        lines.append("# گزارش تحلیل حرفه‌ای EcoCoin v2.0\n")
        lines.append(f"**زمان تحلیل:** {self.report.metadata['scan_time']}\n")
        lines.append(f"**مسیر پروژه:** `{self.report.metadata['project_root']}`\n")
        lines.append(f"**تیم تحلیل:** {', '.join(self.report.metadata['team'])}\n")

        # امتیازات
        lines.append("\n## امتیازات چندبُعدی\n")
        lines.append("| بُعد | امتیاز | وضعیت |")
        lines.append("|------|--------|--------|")
        for dim, score in self.report.scores.items():
            status = "🟢 عالی" if score >= 80 else "🟡 متوسط" if score >= 60 else "🔴 ضعیف"
            lines.append(f"| {dim} | {score}/100 | {status} |")

        # یافته‌های امنیتی
        lines.append("\n## یافته‌های امنیتی\n")
        if self.security_auditor.findings:
            lines.append("| شدت | دسته | فایل | توضیح |")
            lines.append("|------|------|------|--------|")
            for f in self.security_auditor.findings[:20]:  # محدود به ۲۰ مورد
                lines.append(f"| {f.severity} | {f.category} | `{f.file}` | {f.description} |")
        else:
            lines.append("هیچ یافتهٔ امنیتی یافت نشد. ✅")

        # مشکلات معماری
        lines.append("\n## مشکلات معماری\n")
        if self.architect.issues:
            for issue in self.architect.issues[:10]:
                lines.append(f"- **{issue.category}** در `{issue.file}`: {issue.description}")
        else:
            lines.append("هیچ مشکل معماری یافت نشد. ✅")

        # خلاصه
        lines.append("\n## خلاصه\n")
        for key, value in self.report.summary.items():
            lines.append(f"- **{key}:** {value}")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# اجرای اصلی
# ═══════════════════════════════════════════════════════════

def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

    if not root.exists():
        print(f"❌ مسیر {root} وجود ندارد")
        sys.exit(1)

    analyzer = EcoCoinAnalyzer(root)
    report = analyzer.run_full_analysis()

    # ذخیرهٔ گزارش‌ها
    output_dir = root / "reports" / "analysis_v2"
    json_path, md_path = analyzer.save_reports(output_dir)

    # چاپ خلاصه
    print("\n" + "=" * 70)
    print("  خلاصهٔ تحلیل")
    print("=" * 70)
    print(f"\n  امتیاز کلی: {report.scores['overall']}/100")
    print(f"  امنیت: {report.scores['security']}/100")
    print(f"  معماری: {report.scores['architecture']}/100")
    print(f"  داده: {report.scores['data_integrity']}/100")
    print(f"  فرانت‌اند: {report.scores['frontend']}/100")
    print(f"  تست: {report.scores['test_coverage']}/100")
    print(f"  DevOps: {report.scores['devops']}/100")
    print(f"  i18n: {report.scores['i18n']}/100")
    print(f"  عملکرد: {report.scores['performance']}/100")

    print(f"\n  یافته‌های امنیتی: {report.summary['total_security_findings']}")
    print(f"    - بحرانی: {report.summary['critical_findings']}")
    print(f"    - پرخطر: {report.summary['high_findings']}")

    print(f"\n  گزارش JSON: {json_path}")
    print(f"  گزارش Markdown: {md_path}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()