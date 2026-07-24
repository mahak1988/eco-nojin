اسکریپت آنالیز جامع پروژه با قابلیت مقایسه و امنیت بالا

``python
#!/usr/bin/env python3
-- coding: utf-8 --
"""
Econojin Project Analyzer v3.0
==============================
اسکریپت آنالیز جامع با قابلیت:
اسکن ساختار پروژه
تحلیل امنیتی (Security Audit)
تحلیل قراردادهای هوشمند (Smart Contract Analysis)
تحلیل وابستگی‌ها (Dependency Audit)
شناسایی تغییرات (Change Detection)
مقایسه با snapshot قبلی (Diff Analysis)
تولید گزارش‌های JSON/Markdown
پشتیبانی کامل از UTF-8 و فارسی

Usage:
    python analyze_project.py --project D:\\econojin.com
    python analyzeproject.py --project D:\\econojin.com --compare snapshot20260724.json
    python analyze_project.py --project D:\\econojin.com --export json,md
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

═══════════════════════════════════════════════════════════════════════════════
Configuration & Constants
═══════════════════════════════════════════════════════════════════════════════

VERSION = "3.0.0"
DEFAULT_ENCODING = "utf-8"
HASH_ALGORITHM = "sha256"

Directories to ignore during scanning
IGNORE_DIRS: Set[str] = {
    ".git", "node_modules", ".pnpm-store", "pycache",
    ".venv", "venv", ".next", "dist", "build", ".turbo",
    ".cache", ".idea", ".vs", ".syncbackup", "repos",
}

File extensions to analyze
ANALYZABLE_EXTENSIONS: Set[str] = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".sol",
    ".json", ".yaml", ".yml", ".md", ".toml",
}

Security patterns for Python files
PYTHONSECURITYPATTERNS: Dict[str, str] = {
    r"eval\s*\(": "CWE-95: Use of eval() - Code Injection Risk",
    r"exec\s*\(": "CWE-95: Use of exec() - Code Injection Risk",
    r"import\s*\(": "CWE-95: Dynamic import - Potential Code Injection",
    r"pickle\.loads?\(": "CWE-502: Use of pickle - Deserialization Risk",
    r"yaml\.load\s\((?!.Loader)": "CWE-502: Unsafe YAML loading",
    r"subprocess\.(call|run|Popen)\s\([^,],\sshell\s=\s*True": "CWE-78: OS Command Injection",
    r"cursor\.execute\s\([^,]\s\+\s": "CWE-89: SQL Injection",
    r"password\s=\s['\"][^'\"]{1,8}['\"]": "CWE-259: Hardcoded Weak Password",
    r"SECRET_KEY\s=\s['\"][^'\"]{1,16}['\"]": "CWE-798: Hardcoded Secret",
    r"DEBUG\s=\sTrue": "CWE-489: Debug Mode Enabled",
}

Security patterns for Solidity files
SOLIDITYSECURITYPATTERNS: Dict[str, str] = {
    r"\btx\.origin\b": "CWE-477: Use of tx.origin - Phishing Vulnerability",
    r"\bselfdestruct\b": "CWE-672: Use of selfdestruct - Contract Destruction Risk",
    r"\bdelegatecall\b": "CWE-829: Use of delegatecall - Untrusted Code Execution",
    r"\bblock\.timestamp\b.[<>]=?\s\d+": "CWE-330: Timestamp Dependency",
    r"function\s+\w+\s\([^)]\)\spublic\s(?!.*\bonly\w+\b)": "CWE-862: Missing Access Control",
    r"\btransfer\s*\(": "CWE-841: Use of transfer() - 2300 Gas Limit",
    r"\bcall\s\{\svalue\s*:": "CWE-841: Low-level call with value",
    r"\bnow\b": "CWE-330: Deprecated 'now' keyword",
}

Security patterns for TypeScript/JavaScript files
TSSECURITYPATTERNS: Dict[str, str] = {
    r"innerHTML\s*=": "CWE-79: Direct DOM Manipulation - XSS Risk",
    r"dangerouslySetInnerHTML": "CWE-79: React dangerouslySetInnerHTML",
    r"eval\s*\(": "CWE-95: Use of eval() - Code Injection",
    r"localStorage\.setItem\s\([^,]password": "CWE-256: Storing Password in localStorage",
    r"http://": "CWE-319: Cleartext HTTP Transmission",
    r"process\.env\.[A-Z_]+\s\|\|\s['\"][^'\"]{1,8}['\"]": "CWE-798: Hardcoded Fallback Secret",
}

═══════════════════════════════════════════════════════════════════════════════
Data Structures
═══════════════════════════════════════════════════════════════════════════════

class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

@dataclass
class SecurityFinding:
    severity: Severity
    cwe: str
    file: str
    line: int
    description: str
    recommendation: str
    context: str = ""

@dataclass
class ContractAnalysis:
    path: str
    name: str
    functions: List[Dict[str, Any]]
    events: List[Dict[str, Any]]
    modifiers: List[str]
    security_patterns: List[str]
    vulnerabilities: List[SecurityFinding]
    size_kb: float

@dataclass
class DependencyInfo:
    name: str
    version: str
    type: str  # "python", "node", "blockchain"
    hasknownvulnerabilities: bool = False
    is_outdated: bool = False

@dataclass
class FileSnapshot:
    path: str
    hash: str
    size: int
    modified: float
    extension: str

@dataclass
class ProjectSnapshot:
    timestamp: str
    version: str
    total_files: int
    total_size: int
    files: Dict[str, FileSnapshot]
    security_findings: List[SecurityFinding]
    contracts: List[ContractAnalysis]
    dependencies: List[DependencyInfo]

@dataclass
class ChangeRecord:
    file: str
    change_type: str  # "added", "modified", "deleted"
    old_hash: Optional[str]
    new_hash: Optional[str]
    size_diff: int

@dataclass
class AnalysisReport:
    timestamp: str
    version: str
    project_root: str
    structure: Dict[str, Any]
    security_findings: List[SecurityFinding]
    contracts: List[ContractAnalysis]
    dependencies: Dict[str, List[DependencyInfo]]
    changes: List[ChangeRecord]
    statistics: Dict[str, int]
    recommendations: List[str]

═══════════════════════════════════════════════════════════════════════════════
Logging Configuration
═══════════════════════════════════════════════════════════════════════════════

def setup_logging(verbose: bool = False) -> logging.Logger:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s │ %(levelname)-8s │ %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger("project_analyzer")

logger = setup_logging()

═══════════════════════════════════════════════════════════════════════════════
Utility Functions
═══════════════════════════════════════════════════════════════════════════════

def calculatefilehash(filepath: Path, chunksize: int = 8192) -> str:
    """Calculate SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (OSError, PermissionError) as e:
        logger.warning(f"Cannot hash {file_path}: {e}")
        return ""

def should_ignore(path: Path) -> bool:
    """Check if path should be ignored."""
    for part in path.parts:
        if part in IGNOREDIRS or part.startswith(".syncbackup_"):
            return True
    return False

def safereadfile(filepath: Path, encoding: str = DEFAULTENCODING) -> Optional[str]:
    """Safely read file content."""
    try:
        return filepath.readtext(encoding=encoding, errors="replace")
    except Exception as e:
        logger.debug(f"Cannot read {file_path}: {e}")
        return None

def formatsize(sizebytes: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size_bytes)  None:
        """Analyze Python file for security issues."""
        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            for pattern, description in PYTHONSECURITYPATTERNS.items():
                if re.search(pattern, line):
                    cwe = description.split(":")[0]
                    recommendation = self.getrecommendation(cwe)
                    finding = SecurityFinding(
                        severity=self.getseverity(cwe),
                        cwe=cwe,
                        file=str(file_path),
                        line=line_num,
                        description=description,
                        recommendation=recommendation,
                        context=line.strip()[:100]
                    )
                    self.findings.append(finding)

    def analyzesolidityfile(self, file_path: Path, content: str) -> None:
        """Analyze Solidity file for security issues."""
        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            for pattern, description in SOLIDITYSECURITYPATTERNS.items():
                if re.search(pattern, line):
                    cwe = description.split(":")[0]
                    recommendation = self.getrecommendation(cwe)
                    finding = SecurityFinding(
                        severity=self.getseverity(cwe),
                        cwe=cwe,
                        file=str(file_path),
                        line=line_num,
                        description=description,
                        recommendation=recommendation,
                        context=line.strip()[:100]
                    )
                    self.findings.append(finding)

    def analyzetsfile(self, file_path: Path, content: str) -> None:
        """Analyze TypeScript/JavaScript file for security issues."""
        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            for pattern, description in TSSECURITYPATTERNS.items():
                if re.search(pattern, line):
                    cwe = description.split(":")[0]
                    recommendation = self.getrecommendation(cwe)
                    finding = SecurityFinding(
                        severity=self.getseverity(cwe),
                        cwe=cwe,
                        file=str(file_path),
                        line=line_num,
                        description=description,
                        recommendation=recommendation,
                        context=line.strip()[:100]
                    )
                    self.findings.append(finding)

    def getseverity(self, cwe: str) -> Severity:
        """Determine severity based on CWE."""
        critical_cwes = {"CWE-78", "CWE-89", "CWE-95", "CWE-502"}
        high_cwes = {"CWE-79", "CWE-477", "CWE-672", "CWE-829", "CWE-862"}
        medium_cwes = {"CWE-259", "CWE-319", "CWE-330", "CWE-841"}
        
        if cwe in critical_cwes:
            return Severity.CRITICAL
        elif cwe in high_cwes:
            return Severity.HIGH
        elif cwe in medium_cwes:
            return Severity.MEDIUM
        else:
            return Severity.LOW

    def getrecommendation(self, cwe: str) -> str:
        """Get recommendation for CWE."""
        recommendations = {
            "CWE-95": "Avoid eval/exec. Use safer alternatives like ast.literal_eval()",
            "CWE-502": "Use safe_load() for YAML. Avoid pickle for untrusted data",
            "CWE-78": "Use subprocess with shell=False and parameterized commands",
            "CWE-89": "Use parameterized queries or ORM",
            "CWE-79": "Sanitize user input. Use framework-provided escaping",
            "CWE-477": "Use msg.sender instead of tx.origin in Solidity",
            "CWE-672": "Avoid selfdestruct. Use pause mechanism instead",
            "CWE-862": "Add access control modifiers (onlyOwner, onlyAdmin)",
            "CWE-259": "Use environment variables or secret management",
            "CWE-319": "Use HTTPS for all transmissions",
            "CWE-330": "Use Chainlink oracles for time-dependent logic",
            "CWE-841": "Use call() with proper gas management",
            "CWE-256": "Store sensitive data in httpOnly cookies",
            "CWE-798": "Use environment variables for all secrets",
            "CWE-489": "Disable DEBUG in production",
        }
        return recommendations.get(cwe, "Review and fix the identified issue")

═══════════════════════════════════════════════════════════════════════════════
Smart Contract Analyzer
═══════════════════════════════════════════════════════════════════════════════

class ContractAnalyzer:
    """Analyze Solidity smart contracts."""

    def init(self):
        self.contracts: List[ContractAnalysis] = []

    def analyzecontract(self, filepath: Path, content: str) -> ContractAnalysis:
        """Analyze a Solidity contract file."""
        # Extract contract name
        name_match = re.search(r'contract\s+(\w+)', content)
        name = namematch.group(1) if namematch else "Unknown"

        # Extract functions
        functions = []
        func_pattern = r'function\s+(\w+)\s\(([^)])\)\s([\w\s])'
        for match in re.finditer(func_pattern, content):
            func_name, params, modifiers = match.groups()
            visibility = self.extractvisibility(modifiers)
            mutability = self.extractmutability(modifiers)
            functions.append({
                "name": func_name,
                "params": params.strip(),
                "visibility": visibility,
                "mutability": mutability,
            })

        # Extract events
        events = []
        event_pattern = r'event\s+(\w+)\s\(([^)])\)'
        for match in re.finditer(event_pattern, content):
            event_name, params = match.groups()
            events.append({"name": event_name, "params": params.strip()})

        # Extract modifiers
        modifiers = re.findall(r'modifier\s+(\w+)', content)

        # Check security patterns
        securitypatterns = self.checksecuritypatterns(content)

        # Analyze vulnerabilities
        security_analyzer = SecurityAnalyzer()
        securityanalyzer.analyzesolidityfile(filepath, content)
        vulnerabilities = security_analyzer.findings

        contract = ContractAnalysis(
            path=str(file_path),
            name=name,
            functions=functions,
            events=events,
            modifiers=modifiers,
            securitypatterns=securitypatterns,
            vulnerabilities=vulnerabilities,
            sizekb=filepath.stat().st_size / 1024
        )

        self.contracts.append(contract)
        return contract

    def extractvisibility(self, modifiers: str) -> str:
        """Extract function visibility."""
        if "external" in modifiers:
            return "external"
        elif "public" in modifiers:
            return "public"
        elif "internal" in modifiers:
            return "internal"
        elif "private" in modifiers:
            return "private"
        return "public"

    def extractmutability(self, modifiers: str) -> str:
        """Extract function state mutability."""
        if "pure" in modifiers:
            return "pure"
        elif "view" in modifiers:
            return "view"
        elif "payable" in modifiers:
            return "payable"
        return "nonpayable"

    def checksecurity_patterns(self, content: str) -> List[str]:
        """Check for security best practices."""
        patterns = []
        if re.search(r'\brequire\s*\(', content):
            patterns.append("✅ Input Validation (require)")
        if re.search(r'\bemit\s+\w+\(', content):
            patterns.append("✅ Event Logging")
        if re.search(r'\bReentrancyGuard\b', content):
            patterns.append("✅ Reentrancy Protection")
        if re.search(r'\bonlyOwner\b|\bonlyAdmin\b', content):
            patterns.append("✅ Access Control")
        return patterns

═══════════════════════════════════════════════════════════════════════════════
Dependency Analyzer
═══════════════════════════════════════════════════════════════════════════════

class DependencyAnalyzer:
    """Analyze project dependencies."""

    def init(self):
        self.dependencies: Dict[str, List[DependencyInfo]] = {
            "python": [],
            "node": [],
            "blockchain": [],
        }

    def analyzerequirements(self, filepath: Path, content: str) -> None:
        """Analyze Python requirements.txt."""
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Parse package name and version
            match = re.match(r'^([a-zA-Z0-9_-]+)([>= None:
        """Analyze Node.js package.json."""
        try:
            data = json.loads(content)
            
            # Analyze dependencies
            for dep_type in ["dependencies", "devDependencies"]:
                if dep_type in data:
                    for name, version in data[dep_type].items():
                        is_blockchain = any(kw in name.lower() for kw in
                                          ["web3", "ethers", "wagmi", "viem", "rainbowkit"])
                        
                        dep = DependencyInfo(
                            name=name,
                            version=version,
                            type="blockchain" if is_blockchain else "node"
                        )
                        self.dependencies["blockchain" if is_blockchain else "node"].append(dep)
        except json.JSONDecodeError as e:
            logger.warning(f"Cannot parse {file_path}: {e}")

═══════════════════════════════════════════════════════════════════════════════
Project Analyzer
═══════════════════════════════════════════════════════════════════════════════

class ProjectAnalyzer:
    """Main project analyzer."""

    def init(self, project_root: Path):
        self.projectroot = projectroot
        self.security_analyzer = SecurityAnalyzer()
        self.contract_analyzer = ContractAnalyzer()
        self.dependency_analyzer = DependencyAnalyzer()
        self.files: Dict[str, FileSnapshot] = {}
        self.statistics: Dict[str, int] = defaultdict(int)

    def analyze(self, compare_snapshot: Optional[Path] = None) -> AnalysisReport:
        """Perform complete project analysis."""
        logger.info(f"Starting analysis of {self.project_root}")
        
        # Scan project structure
        self.scanstructure()
        
        # Analyze files
        self.analyzefiles()
        
        # Detect changes if snapshot provided
        changes = []
        if comparesnapshot and comparesnapshot.exists():
            changes = self.detectchanges(compare_snapshot)
        
        # Generate recommendations
        recommendations = self.generaterecommendations()
        
        report = AnalysisReport(
            timestamp=datetime.now().isoformat(),
            version=VERSION,
            projectroot=str(self.projectroot),
            structure=self.getstructure_summary(),
            securityfindings=self.securityanalyzer.findings,
            contracts=self.contract_analyzer.contracts,
            dependencies=self.dependency_analyzer.dependencies,
            changes=changes,
            statistics=dict(self.statistics),
            recommendations=recommendations
        )
        
        logger.info("Analysis complete")
        return report

    def scanstructure(self) -> None:
        """Scan project structure."""
        logger.info("Scanning project structure...")
        
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            
            # Filter ignored directories
            dirs[:] = [d for d in dirs if not shouldignore(rootpath / d)]
            
            for file_name in files:
                filepath = rootpath / file_name
                
                if shouldignore(filepath):
                    continue
                
                try:
                    stat = file_path.stat()
                    filehash = calculatefilehash(filepath)
                    
                    snapshot = FileSnapshot(
                        path=str(filepath.relativeto(self.project_root)),
                        hash=file_hash,
                        size=stat.st_size,
                        modified=stat.st_mtime,
                        extension=file_path.suffix.lower()
                    )
                    
                    self.files[snapshot.path] = snapshot
                    self.statistics["total_files"] += 1
                    self.statistics["totalsize"] += stat.stsize
                    self.statistics[f"files_{snapshot.extension}"] += 1
                    
                except Exception as e:
                    logger.debug(f"Cannot process {file_path}: {e}")

    def analyzefiles(self) -> None:
        """Analyze all files."""
        logger.info("Analyzing files...")
        
        for filepathstr, snapshot in self.files.items():
            filepath = self.projectroot / filepathstr
            
            if not file_path.exists():
                continue
            
            content = safereadfile(file_path)
            if not content:
                continue
            
            # Security analysis
            if file_path.suffix == ".py":
                self.securityanalyzer.analyzepythonfile(filepath, content)
            elif file_path.suffix == ".sol":
                self.contractanalyzer.analyzecontract(file_path, content)
            elif file_path.suffix in [".ts", ".tsx", ".js", ".jsx"]:
                self.securityanalyzer.analyzetsfile(filepath, content)
            
            # Dependency analysis
            if file_path.name == "requirements.txt":
                self.dependencyanalyzer.analyzerequirements(file_path, content)
            elif file_path.name == "package.json":
                self.dependencyanalyzer.analyzepackagejson(filepath, content)

    def detectchanges(self, snapshot_path: Path) -> List[ChangeRecord]:
        """Detect changes compared to previous snapshot."""
        logger.info(f"Comparing with snapshot: {snapshot_path}")
        
        try:
            with open(snapshotpath, "r", encoding=DEFAULTENCODING) as f:
                old_data = json.load(f)
            
            oldfiles = {f["path"]: f for f in olddata.get("files", [])}
            changes = []
            
            # Check for modified and deleted files
            for path, oldsnapshot in oldfiles.items():
                if path in self.files:
                    new_snapshot = self.files[path]
                    if oldsnapshot["hash"] != newsnapshot.hash:
                        changes.append(ChangeRecord(
                            file=path,
                            change_type="modified",
                            oldhash=oldsnapshot["hash"],
                            newhash=newsnapshot.hash,
                            sizediff=newsnapshot.size - old_snapshot["size"]
                        ))
                else:
                    changes.append(ChangeRecord(
                        file=path,
                        change_type="deleted",
                        oldhash=oldsnapshot["hash"],
                        new_hash=None,
                        sizediff=-oldsnapshot["size"]
                    ))
            
            # Check for new files
            for path, new_snapshot in self.files.items():
                if path not in old_files:
                    changes.append(ChangeRecord(
                        file=path,
                        change_type="added",
                        old_hash=None,
                        newhash=newsnapshot.hash,
                        sizediff=newsnapshot.size
                    ))
            
            logger.info(f"Detected {len(changes)} changes")
            return changes
            
        except Exception as e:
            logger.error(f"Cannot compare with snapshot: {e}")
            return []

    def getstructure_summary(self) -> Dict[str, Any]:
        """Get project structure summary."""
        dirs = defaultdict(int)
        
        for path in self.files.keys():
            parts = Path(path).parts
            if len(parts) > 1:
                dirs[parts[0]] += 1
        
        return {
            "totalfiles": self.statistics["totalfiles"],
            "totalsize": self.statistics["totalsize"],
            "totalsizehuman": formatsize(self.statistics["totalsize"]),
            "directories": dict(dirs),
            "file_types": {
                k.replace("files_", ""): v 
                for k, v in self.statistics.items() 
                if k.startswith("files_")
            }
        }

    def generaterecommendations(self) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Security recommendations
        criticalfindings = [f for f in self.securityanalyzer.findings 
                           if f.severity == Severity.CRITICAL]
        if critical_findings:
            recommendations.append(
                f"🔴 CRITICAL: {len(critical_findings)} critical security issues found. "
                "Immediate action required."
            )
        
        highfindings = [f for f in self.securityanalyzer.findings 
                        if f.severity == Severity.HIGH]
        if high_findings:
            recommendations.append(
                f"🟠 HIGH: {len(high_findings)} high-severity security issues found. "
                "Should be addressed soon."
            )
        
        # Contract recommendations
        for contract in self.contract_analyzer.contracts:
            if "✅ Reentrancy Protection" not in contract.security_patterns:
                recommendations.append(
                    f"📜 Contract {contract.name}: Missing ReentrancyGuard. "
                    "Consider adding OpenZeppelin's ReentrancyGuard."
                )
            
            if "✅ Access Control" not in contract.security_patterns:
                recommendations.append(
                    f"📜 Contract {contract.name}: Missing access control. "
                    "Add onlyOwner or similar modifiers."
                )
        
        # General recommendations
        if self.statistics["total_files"] > 10000:
            recommendations.append(
                "📁 Large project detected (>10,000 files). "
                "Consider modularizing or using a monorepo tool."
            )
        
        return recommendations

    def savesnapshot(self, outputpath: Path) -> None:
        """Save current state as snapshot."""
        snapshot_data = {
            "timestamp": datetime.now().isoformat(),
            "version": VERSION,
            "totalfiles": self.statistics["totalfiles"],
            "totalsize": self.statistics["totalsize"],
            "files": [asdict(f) for f in self.files.values()],
        }
        
        with open(outputpath, "w", encoding=DEFAULTENCODING) as f:
            json.dump(snapshotdata, f, ensureascii=False, indent=2)
        
        logger.info(f"Snapshot saved to {output_path}")

═══════════════════════════════════════════════════════════════════════════════
Report Generator
═══════════════════════════════════════════════════════════════════════════════

class ReportGenerator:
    """Generate analysis reports."""

    @staticmethod
    def generatejsonreport(report: AnalysisReport, output_path: Path) -> None:
        """Generate JSON report."""
        report_dict = asdict(report)
        
        # Convert enums to strings
        for finding in reportdict["securityfindings"]:
            finding["severity"] = finding["severity"].value
        
        with open(outputpath, "w", encoding=DEFAULTENCODING) as f:
            json.dump(reportdict, f, ensureascii=False, indent=2)
        
        logger.info(f"JSON report saved to {output_path}")

    @staticmethod
    def generatemarkdownreport(report: AnalysisReport, output_path: Path) -> None:
        """Generate Markdown report."""
        md = []
        
        # Header
        md.append("# 📊 Econojin Project Analysis Report\n")
        md.append(f"Version: {report.version}  ")
        md.append(f"Timestamp: {report.timestamp}  ")
        md.append(f"Project Root: {report.project_root}\n")
        
        # Statistics
        md.append("## 📈 Statistics\n")
        md.append(f"- Total Files: {report.statistics['total_files']:,}")
        md.append(f"- Total Size: {formatsize(report.statistics['totalsize'])}")
        md.append(f"- Security Findings: {len(report.security_findings)}")
        md.append(f"- Smart Contracts: {len(report.contracts)}\n")
        
        # File Types
        md.append("### File Types\n")
        md.append("| Extension | Count |")
        md.append("|-----------|-------|")
        for ext, count in sorted(report.structure["file_types"].items(), 
                                key=lambda x: x[1], reverse=True)[:15]:
            md.append(f"| {ext} | {count:,} |")
        md.append("")
        
        # Security Findings
        if report.security_findings:
            md.append("## 🔒 Security Findings\n")
            
            # Group by severity
            by_severity = defaultdict(list)
            for finding in report.security_findings:
                by_severity[finding.severity.value].append(finding)
            
            for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                if severity in by_severity:
                    md.append(f"### {severity} ({len(by_severity[severity])})\n")
                    for finding in by_severity[severity][:10]:  # Limit to 10
                        md.append(f"- {finding.cwe} in {finding.file}:{finding.line}")
                        md.append(f"  - {finding.description}")
                        md.append(f"  - Recommendation: {finding.recommendation}")
                    if len(by_severity[severity]) > 10:
                        md.append(f"- ... and {len(by_severity[severity]) - 10} more")
                    md.append("")
        
        # Smart Contracts
        if report.contracts:
            md.append("## 📜 Smart Contracts\n")
            for contract in report.contracts:
                md.append(f"### {contract.name}\n")
                md.append(f"- Path: {contract.path}")
                md.append(f"- Size: {contract.size_kb:.2f} KB")
                md.append(f"- Functions: {len(contract.functions)}")
                md.append(f"- Events: {len(contract.events)}")
                if contract.security_patterns:
                    md.append("- Security Patterns:")
                    for pattern in contract.security_patterns:
                        md.append(f"  - {pattern}")
                md.append("")
        
        # Changes
        if report.changes:
            md.append("## 🔄 Changes Detected\n")
            
            added = [c for c in report.changes if c.change_type == "added"]
            modified = [c for c in report.changes if c.change_type == "modified"]
            deleted = [c for c in report.changes if c.change_type == "deleted"]
            
            if added:
                md.append(f"### ➕ Added ({len(added)})\n")
                for change in added[:20]:
                    md.append(f"- {change.file} ({formatsize(change.sizediff)})")
                if len(added) > 20:
                    md.append(f"- ... and {len(added) - 20} more")
                md.append("")
            
            if modified:
                md.append(f"### ✏️ Modified ({len(modified)})\n")
                for change in modified[:20]:
                    diff = change.size_diff
                    sign = "+" if diff > 0 else ""
                    md.append(f"- {change.file} ({sign}{format_size(diff)})")
                if len(modified) > 20:
                    md.append(f"- ... and {len(modified) - 20} more")
                md.append("")
            
            if deleted:
                md.append(f"### ❌ Deleted ({len(deleted)})\n")
                for change in deleted[:20]:
                    md.append(f"- {change.file}`")
                if len(deleted) > 20:
                    md.append(f"- ... and {len(deleted) - 20} more")
                md.append("")
        
        # Recommendations
        if report.recommendations:
            md.append("## 💡 Recommendations\n")
            for rec in report.recommendations:
                md.append(f"- {rec}")
            md.append("")
        
        # Write to file
        with open(outputpath, "w", encoding=DEFAULTENCODING) as f:
            f.write("\n".join(md))
        
        logger.info(f"Markdown report saved to {output_path}")

    @staticmethod
    def printconsolesummary(report: AnalysisReport) -> None:
        """Print summary to console."""
        print("\n" + "=" * 70)
        print("  📊 ECONOJIN PROJECT ANALYSIS SUMMARY")
        print("=" * 70)
        
        print(f"\n  📁 Project: {report.project_root}")
        print(f"  📅 Timestamp: {report.timestamp}")
        
        print(f"\n  📈 Statistics:")
        print(f"    • Total Files: {report.statistics['total_files']:,}")
        print(f"    • Total Size: {formatsize(report.statistics['totalsize'])}")
        
        # Security summary
        if report.security_findings:
            print(f"\n  🔒 Security Findings: {len(report.security_findings)}")
            by_severity = defaultdict(int)
            for finding in report.security_findings:
                by_severity[finding.severity.value] += 1
            
            for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                if severity in by_severity:
                    icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}[severity]
                    print(f"    {icon} {severity}: {by_severity[severity]}")
        
        # Contracts summary
        if report.contracts:
            print(f"\n  📜 Smart Contracts: {len