#!/usr/bin/env python3
"""
Phase 1 Security Hardening & Zero Trust Pipeline (Final)
Single file, Windows/Python 3.13+ compatible, zero external dependencies.
Checks: EnvVal -> SBOM -> SecretScan -> mTLS
"""

import abc
import json
import logging
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Phase1Security")


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Finding:
    severity: str
    category: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    recommendation: str = ""


@dataclass
class Result:
    check_name: str
    status: str
    score: float
    findings: List[Finding] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class BaseChecker(abc.ABC):
    def __init__(self, root: Path, cfg: Dict):
        self.root = root.resolve()
        self.cfg = cfg
        self.ignore = {
            ".git", ".venv", "venv", "env", ".env", "__pycache__",
            "tutorial_env", "node_modules", ".next", "dist", "build",
            "out", ".pnpm-store", ".cache", ".vscode", ".idea",
            ".pytest_cache", "site-packages", "_vendor"
        }
        self.skip_ext = {
            ".pyc", ".so", ".dll", ".exe", ".bin", ".zip", ".tar",
            ".gz", ".jpg", ".png", ".pdf", ".db", ".sqlite"
        }

    @abc.abstractmethod
    def run(self) -> Result:
        pass

    def _ign(self, p: Path) -> bool:
        try:
            ps = str(p).lower().replace("\\", "/")
            rs = str(self.root).lower().replace("\\", "/")
            if not ps.startswith(rs + "/") and ps != rs:
                return True
            for ig in self.ignore:
                if f"/{ig}/" in ps or ps.endswith(f"/{ig}"):
                    return True
            return "/site-packages/" in ps or "/_vendor/" in ps
        except Exception:
            return True

    def _cmd(self, cmd: list, timeout: int = 30) -> Tuple[int, str, str]:
        try:
            si = None
            if sys.platform == "win32":
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            r = subprocess.run(
                cmd, capture_output=True, text=True, check=False,
                timeout=timeout, startupinfo=si,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            return r.returncode, r.stdout, r.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Timeout {timeout}s"
        except FileNotFoundError:
            return -1, "", f"Cmd not found: {cmd[0]}"
        except Exception as e:
            return -1, "", f"{type(e).__name__}: {e}"

    def _rel(self, p: Path) -> str:
        try:
            return str(p.relative_to(self.root)).replace("\\", "/")
        except Exception:
            return str(p).replace("\\", "/")


class EnvVal(BaseChecker):
    REQ = {"DATABASE_URL": "Database connection", "SECRET_KEY": "JWT/Session key"}
    SENS = {"PRIVATE_KEY", "API_KEY", "SECRET", "PASSWORD", "TOKEN", "CREDENTIAL"}
    PH = ["your_", "example", "todo", "changeme", "placeholder", "_here", "${"]

    def _read_safe(self, path: Path) -> str:
        encodings = ['utf-8-sig', 'utf-16', 'utf-8', 'latin-1']
        for enc in encodings:
            try:
                return path.read_text(encoding=enc, errors='strict')
            except (UnicodeDecodeError, LookupError):
                continue
        return path.read_text(encoding='utf-8', errors='replace')

    def _ph(self, v: str) -> bool:
        v = v.strip().strip('"').strip("'")
        if not v or v.lower() in ["none", "null", ""]:
            return True
        return any(p in v.lower() for p in self.PH)

    def run(self) -> Result:
        findings = []
        ep = self.root / ".env"
        if not ep.exists():
            findings.append(Finding("HIGH", "EnvMissing", ".env file not found", None, None, "Create .env based on template and fill real values"))
            return Result("EnvVal", "FAIL", 0.0, findings, {"exists": False})
        try:
            txt = self._read_safe(ep)
            lines = [l.strip() for l in txt.splitlines() if l.strip() and not l.startswith("#")]
            ev = {}
            for l in lines:
                if "=" in l:
                    k, _, v = l.partition("=")
                    ev[k.strip()] = v.strip().strip('"').strip("'")
            for k, d in self.REQ.items():
                if k not in ev:
                    findings.append(Finding("MEDIUM", "EnvMissingKey", f"Required key {k} ({d}) not defined", ".env", None, f"Add {k}=real_value to .env"))
            pc = sum(1 for k, v in ev.items() if any(x in k.upper() for x in self.SENS) and self._ph(v))
            for k, v in ev.items():
                if any(x in k.upper() for x in self.SENS) and self._ph(v):
                    findings.append(Finding("INFO", "EnvPlaceholder", f"Sensitive key {k} has placeholder value", ".env", None, "Replace with real value before production"))
            score = 1.0
            if any(f.severity == "HIGH" for f in findings):
                score = 0.3
            elif pc > 2:
                score = 0.7
            return Result("EnvVal", "PASS" if score >= 0.8 else "WARN" if score >= 0.5 else "FAIL", score, findings, {"exists": True, "total": len(ev), "placeholder": pc})
        except Exception as e:
            return Result("EnvVal", "FAIL", 0.0, [Finding("CRITICAL", "EnvError", f"Error reading .env: {e}")], {"exists": True, "error": str(e)})


class SBOM(BaseChecker):
    def run(self) -> Result:
        deps = []
        score = 1.0
        findings = []
        for fp in [self.root / "requirements.txt", self.root / "poetry.lock", self.root / "pyproject.toml"]:
            if not fp.exists():
                continue
            try:
                txt = fp.read_text(encoding="utf-8", errors="ignore")
                if fp.name == "requirements.txt":
                    deps = [
                        {"name": ln.split("==")[0].split(">=")[0].strip(),
                         "version": ln.split("==")[1] if "==" in ln else "unknown"}
                        for ln in txt.splitlines() if ln.strip() and not ln.startswith("#")
                    ]
                elif fp.name == "poetry.lock":
                    deps = [{"name": m, "version": "unknown"} for m in re.findall(r'name\s*=\s*"([^"]+)"', txt)]
                elif fp.name == "pyproject.toml":
                    sec = re.search(r'\[project\.dependencies\](.*?)(?=\n\[|\Z)', txt, re.DOTALL)
                    if sec:
                        deps = [{"name": m, "version": "unknown"} for m in re.findall(r'^\s*([a-zA-Z0-9_-]+)\s*[=<>]', sec.group(1), re.MULTILINE)]
                break
            except Exception:
                continue
        if not deps:
            rc, out, _ = self._cmd([sys.executable, "-m", "pip", "list", "--format=json"])
            if rc == 0 and out.strip():
                deps = json.loads(out)
        if not deps:
            findings.append(Finding("MEDIUM", "SBOM", "No valid dependency file found", ".", "", "Use requirements.txt or pyproject.toml"))
            score = 0.5
        return Result("SBOM", "PASS" if score >= 0.7 else "WARN" if score >= 0.4 else "FAIL", score, findings, {"total": len(deps), "at": datetime.now(timezone.utc).isoformat()})


class SecretScan(BaseChecker):
    PATS = [
        (re.compile(r'(?i)(?:aws_access_key_id|aws_secret_access_key)\s*[:=]\s*[A-Z0-9/+=]{20,}'), "AWS"),
        (re.compile(r'-----BEGIN(?: RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----'), "PrivateKey"),
        (re.compile(r'(?i)(?:ghp_|glpat-)[a-zA-Z0-9]{36,}'), "VCSToken"),
        (re.compile(r'(?i)(?:api_key|apikey|secret|token|password)\s*[:=]\s*["\']?[a-zA-Z0-9_\-]{16,}["\']?'), "Generic"),
        (re.compile(r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'), "JWT")
    ]
    PH = ["your_", "example", "todo", "changeme", "placeholder", "_here", "${", "xxx", "***", "<", ">", "replace"]

    def _ph(self, v: str) -> bool:
        v = v.strip().strip('"').strip("'")
        if not v or v.lower() in ["none", "null", ""]:
            return True
        if any(p in v.lower() for p in self.PH):
            return True
        if len(v) < 20 and re.match(r'^[a-zA-Z0-9_-]+$', v):
            return True
        return False

    def run(self) -> Result:
        findings = []
        crit = False
        scanned = skipped = 0
        exts = {'.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.env', '.sh', '.bat', '.ps1', '.md', '.txt'}
        for fp in self.root.rglob("*"):
            try:
                if not fp.is_file() or self._ign(fp) or fp.suffix.lower() not in exts or fp.stat().st_size > 500 * 1024:
                    skipped += 1
                    continue
                try:
                    txt = fp.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    skipped += 1
                    continue
                scanned += 1
                rp = self._rel(fp)
                for ln_n, ln in enumerate(txt.splitlines(), 1):
                    st = ln.strip()
                    if not st or st.startswith(('#', '//', '/*', '*', 'import ', 'from ', 'require(', 'const ', 'let ', 'var ')):
                        continue
                    if re.match(r'^(?:api_key|token|secret|password)\s*[:=]\s*["\']?$', st, re.I):
                        continue
                    for pat, cat in self.PATS:
                        m = pat.search(ln)
                        if m:
                            val = re.search(r'[:=]\s*["\']?([^"\'#\n]+)', m.group(0))
                            if val and self._ph(val.group(1)):
                                continue
                            crit = True
                            findings.append(Finding("CRITICAL", f"Secret/{cat}", f"Secret pattern detected ({cat})", rp, ln_n, "Remove secret and use os.getenv() + Vault"))
                            break
            except Exception:
                skipped += 1
                continue
        score = 0.0 if crit else (0.6 if findings else 1.0)
        return Result("SecretScan", "FAIL" if score == 0.0 else "WARN" if score < 1.0 else "PASS", score, findings, {"scanned": scanned, "skipped": skipped, "time": round(time.time() % 3600, 2)})


class mTLS(BaseChecker):
    def run(self) -> Result:
        findings = []
        certs = []
        score = 1.0
        openssl_ok = False
        for pat in ["*.pem", "*.crt", "*.cert", "*.cer", "*.key"]:
            try:
                certs.extend(self.root.rglob(pat))
            except Exception:
                continue
        certs = list(set(c for c in certs if not self._ign(c)))
        rc, _, _ = self._cmd(["openssl", "version"])
        openssl_ok = (rc == 0)
        if not certs:
            findings.append(Finding("INFO", "mTLS", "No TLS certificate found (may use SPIFFE/SPIRE)", None, None, "Ensure mTLS is implemented for Zero Trust"))
            score = 0.9
        else:
            for cp in certs:
                try:
                    rp = self._rel(cp)
                    if openssl_ok:
                        rc, out, _ = self._cmd(["openssl", "x509", "-enddate", "-noout", "-in", str(cp)], timeout=10)
                        if rc == 0 and "notAfter=" in out:
                            ds = out.strip().replace("notAfter=", "")
                            for fmt in ["%b %d %H:%M:%S %Y %Z", "%b  %d %H:%M:%S %Y %Z", "%Y-%m-%d %H:%M:%S"]:
                                try:
                                    ed = datetime.strptime(ds, fmt).replace(tzinfo=timezone.utc)
                                    dl = (ed - datetime.now(timezone.utc)).days
                                    if dl < 0:
                                        findings.append(Finding("CRITICAL", "mTLS", f"Certificate expired: {cp.name}", rp, None, "Renew certificate immediately"))
                                        score = 0.0
                                    elif dl < 30:
                                        findings.append(Finding("HIGH", "mTLS", f"Certificate expiring soon ({dl} days): {cp.name}", rp, None, "Plan certificate renewal"))
                                        score = min(score, 0.7)
                                    break
                                except ValueError:
                                    continue
                except Exception:
                    continue
        return Result("mTLS", "FAIL" if score < 0.6 else "WARN" if score < 1.0 else "PASS", score, findings, {"certs": len(certs), "openssl": openssl_ok, "platform": sys.platform})


class Pipeline:
    def __init__(self, root: Path, fail_on_critical: bool = True):
        self.root = root.resolve()
        self.fail_on_critical = fail_on_critical
        self.checks = [EnvVal(self.root, {}), SBOM(self.root, {}), SecretScan(self.root, {}), mTLS(self.root, {})]

    def run(self) -> Dict:
        logger.info(f"Starting Phase 1 Security Pipeline | Root: {self.root} | Platform: {sys.platform}")
        results = []
        has_crit = False
        t0 = time.time()
        for chk in self.checks:
            nm = chk.__class__.__name__
            logger.info(f"Running check: {nm}")
            try:
                r = chk.run()
                results.append(asdict(r))
                for f in r.findings:
                    if f.severity in ["CRITICAL", "HIGH"]:
                        logger.warning(f"[{f.severity}] {f.category}: {f.message} ({f.file_path})")
                if any(f.severity == Severity.CRITICAL for f in r.findings):
                    has_crit = True
            except Exception as e:
                logger.error(f"Error in {nm}: {type(e).__name__}: {e}")
                results.append(asdict(Result(nm, "FAIL", 0.0, [Finding("CRITICAL", "PipelineError", f"{type(e).__name__}: {e}")])))
                has_crit = True
        elapsed = time.time() - t0
        overall = sum(r["score"] for r in results) / len(results) if results else 0.0
        report = {
            "version": "1.0-final",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_score": round(overall, 3),
            "status": "PASS" if not has_crit else ("WARN" if any(r["status"] == "WARN" for r in results) else "FAIL"),
            "time_sec": round(elapsed, 2),
            "checks": results,
            "zero_trust": "READY" if overall >= 0.8 else "NEEDS_ATTENTION",
            "next": [f"Fix: {r['check_name']} - {r['findings'][0]['message']}" for r in results if r["status"] == "FAIL"] or [f"Improve: {r['check_name']} - {r['findings'][0]['recommendation']}" for r in results if r["status"] == "WARN"] or ["Proceed to Phase 2"]
        }
        rp = self.root / "phase1_security_report.json"
        try:
            with open(rp, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Report saved: {rp}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
        if self.fail_on_critical and has_crit:
            logger.error("Critical finding detected - pipeline stopped")
            sys.exit(1)
        logger.info(f"Pipeline complete | Score: {overall:.2f} | Status: {report['status']} | Time: {elapsed:.1f}s")
        return report


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Phase 1 Security Pipeline - Single file, Windows-compatible")
    ap.add_argument("--root", type=Path, default=Path("."), help="Project root path")
    ap.add_argument("--allow-warnings", action="store_true", help="Stop only on CRITICAL, not WARN")
    ap.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    args = ap.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    if not args.root.exists():
        logger.error(f"Path does not exist: {args.root.absolute()}")
        sys.exit(2)
    Pipeline(args.root.resolve(), fail_on_critical=not args.allow_warnings).run()


if __name__ == "__main__":
    main()