#!/usr/bin/env python3
"""
Phase 3 Blockchain & Token Economy Readiness Assessment (Final)
Single file, Windows/Python 3.13+ compatible, zero external dependencies.
Checks: L2Scalability -> TokenEconomy -> SmartContractSecurity -> PQCReadiness
Optimized: Fast scan, multi-language support (.py, .sol, .rs, .json, .yaml), focused patterns.
"""

import abc
import json
import logging
import os
import re
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
logger = logging.getLogger("Phase3BlockchainToken")


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
            ".pytest_cache", "site-packages", "_vendor", ".eggs",
            "coverage", "htmlcov", ".mypy_cache", "logs", "temp", "artifacts", "cache"
        }
        self.target_ext = {'.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml', '.toml', '.sol', '.rs', '.cairo'}
        self.max_files = 100
        self.max_file_size = 250 * 1024

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

    def _scan_patterns(self, patterns: Dict[str, List[re.Pattern]], limit_files: Optional[int] = None) -> Tuple[Dict[str, int], int]:
        counts = {k: 0 for k in patterns}
        scanned = 0
        max_files = limit_files or self.max_files
        
        for fp in self.root.rglob("*"):
            if scanned >= max_files:
                break
            try:
                if not fp.is_file() or self._ign(fp) or fp.suffix.lower() not in self.target_ext:
                    continue
                if fp.stat().st_size > self.max_file_size:
                    continue
                txt = fp.read_text(encoding="utf-8", errors="ignore")
                for cat, pats in patterns.items():
                    for pat in pats:
                        if pat.search(txt):
                            counts[cat] += 1
                            break
                scanned += 1
            except (PermissionError, UnicodeDecodeError, OSError):
                continue
            except Exception:
                continue
        return counts, scanned

    def _calc_score(self, found: int, total: int, threshold: float = 0.6) -> Tuple[float, str]:
        if total == 0:
            return 1.0, "PASS"
        score = min(found / total, 1.0)
        status = "PASS" if score >= 0.7 else ("WARN" if score >= threshold else "FAIL")
        return score, status


class L2ScalabilityChecker(BaseChecker):
    def run(self) -> Result:
        patterns = {
            "RollupArchitecture": [
                re.compile(r'\b(zk_rollup|zk_evm|optimistic_rollup|validium|plasma)\b', re.I),
                re.compile(r'da_layer|data_availability|batch_submission', re.I)
            ],
            "ConsensusOptimization": [
                re.compile(r'consensus_mech|pbft_opt|dag_consensus|gossipsub', re.I),
                re.compile(r'finality_target|block_time_ms|tps_target', re.I)
            ],
            "StateManagement": [
                re.compile(r'state_root|merkle_patricia|sparse_merkle', re.I),
                re.compile(r'state_sync|snap_sync|archive_node', re.I)
            ],
            "BridgeInterop": [
                re.compile(r'cross_chain|bridge_protocol|message_passing', re.I),
                re.compile(r'interop_layer|l2_router|canonical_bridge', re.I)
            ]
        }
        counts, scanned = self._scan_patterns(patterns, limit_files=50)
        total = len(patterns)
        found = sum(1 for v in counts.values() if v > 0)
        score, status = self._calc_score(found, total)
        
        findings = []
        if counts["RollupArchitecture"] == 0:
            findings.append(Finding("MEDIUM", "Missing", "No L2/Rollup architecture pattern detected", None, None, "Define ZK or Optimistic Rollup strategy for L2 scaling"))
        if counts["ConsensusOptimization"] == 0:
            findings.append(Finding("LOW", "Missing", "No consensus or TPS optimization targets found", None, None, "Set explicit finality (<2s) and throughput (>10k TPS) targets"))
        
        return Result("L2Scalability", status, score, findings, {
            "scanned": scanned, "indicators_found": found, "details": counts
        })


class TokenEconomyChecker(BaseChecker):
    def run(self) -> Result:
        patterns = {
            "TokenomicsDesign": [
                re.compile(r'\b(token_economy|tokenomics|supply_schedule|vesting_cliff)\b', re.I),
                re.compile(r'mint_burn|inflation_rate|staking_yield', re.I)
            ],
            "AgentPayments": [
                re.compile(r'micro_payment|agent_reward|service_fee|compute_credit', re.I),
                re.compile(r'erc4337|account_abstraction|paymaster', re.I)
            ],
            "IncentiveMechanism": [
                re.compile(r'liquidity_mining|reward_pool|bounty_system', re.I),
                re.compile(r'slashing_condition|bond_requirement|dispute_resolution', re.I)
            ],
            "Governance": [
                re.compile(r'proposal_system|voting_weight|quorum_requirement', re.I),
                re.compile(r'dao_framework|treasury_multi_sig|snapshot_integration', re.I)
            ]
        }
        counts, scanned = self._scan_patterns(patterns, limit_files=50)
        total = len(patterns)
        found = sum(1 for v in counts.values() if v > 0)
        score, status = self._calc_score(found, total)
        
        findings = []
        if counts["AgentPayments"] == 0:
            findings.append(Finding("MEDIUM", "Missing", "No agent payment or microtransaction pattern detected", None, None, "Implement ERC-4337/Account Abstraction for seamless agent-to-agent payments"))
        if counts["TokenomicsDesign"] == 0:
            findings.append(Finding("LOW", "Missing", "No token supply or economic model pattern found", None, None, "Define clear minting, burning, and vesting schedules"))
        
        return Result("TokenEconomy", status, score, findings, {
            "scanned": scanned, "indicators_found": found, "details": counts
        })


class SmartContractSecurityChecker(BaseChecker):
    def run(self) -> Result:
        patterns = {
            "AccessControl": [
                re.compile(r'only_owner|access_control|role_based|permission_guard', re.I),
                re.compile(r'multi_sig|timelock|upgrade_proxy', re.I)
            ],
            "VulnerabilityProtection": [
                re.compile(r'reentrancy_guard|non_reentrant|checks_effects_interactions', re.I),
                re.compile(r'integer_overflow|safe_math|bounds_check', re.I)
            ],
            "AuditAutomation": [
                re.compile(r'slither|foundry_test|echidna|formal_verif', re.I),
                re.compile(r'invariant_test|fuzz_target|coverage_report', re.I)
            ],
            "EmergencyStop": [
                re.compile(r'pausable|circuit_breaker|emergency_pause', re.I),
                re.compile(r'admin_override|pause_guard|rescue_fund', re.I)
            ]
        }
        counts, scanned = self._scan_patterns(patterns, limit_files=50)
        total = len(patterns)
        found = sum(1 for v in counts.values() if v > 0)
        score, status = self._calc_score(found, total)
        
        findings = []
        if counts["VulnerabilityProtection"] == 0:
            findings.append(Finding("HIGH", "Missing", "No reentrancy or overflow protection pattern detected", None, None, "Implement ReentrancyGuard and SafeMath/built-in overflow checks"))
        if counts["AuditAutomation"] == 0:
            findings.append(Finding("MEDIUM", "Missing", "No automated audit or formal verification pattern found", None, None, "Integrate Slither/Foundry fuzzing into CI/CD pipeline"))
        
        return Result("SmartContractSecurity", status, score, findings, {
            "scanned": scanned, "indicators_found": found, "details": counts
        })


class PQCReadinessChecker(BaseChecker):
    def run(self) -> Result:
        patterns = {
            "KyberKEM": [
                re.compile(r'\b(kyber|ml_kem|crystals_kem)\b', re.I),
                re.compile(r'key_encapsulation|kem_encrypt|pqc_kem', re.I)
            ],
            "DilithiumSig": [
                re.compile(r'\b(dilithium|ml_dsa|crystals_sig)\b', re.I),
                re.compile(r'digital_signature|pqc_sign|lattice_sig', re.I)
            ],
            "CryptoAgility": [
                re.compile(r'crypto_agility|algorithm_switch|hybrid_cipher', re.I),
                re.compile(r'key_rotation|cipher_suite|pqc_migration', re.I)
            ],
            "KeyManagement": [
                re.compile(r'key_lifecycle|hsm_integration|secure_enclave', re.I),
                re.compile(r'key_derivation|hd_wallet|threshold_sig', re.I)
            ]
        }
        counts, scanned = self._scan_patterns(patterns, limit_files=50)
        total = len(patterns)
        found = sum(1 for v in counts.values() if v > 0)
        score, status = self._calc_score(found, total)
        
        findings = []
        if counts["KyberKEM"] == 0 and counts["DilithiumSig"] == 0:
            findings.append(Finding("HIGH", "Missing", "No Post-Quantum Cryptography patterns detected", None, None, "Plan migration to Kyber (KEM) and Dilithium (Signatures) per NIST 2026 standards"))
        if counts["CryptoAgility"] == 0:
            findings.append(Finding("MEDIUM", "Missing", "No crypto-agility or hybrid cipher pattern found", None, None, "Implement hybrid classical/PQC signature scheme for transition period"))
        
        return Result("PQCReadiness", status, score, findings, {
            "scanned": scanned, "indicators_found": found, "details": counts
        })


class Pipeline:
    def __init__(self, root: Path, fail_on_critical: bool = True):
        self.root = root.resolve()
        self.fail_on_critical = fail_on_critical
        self.checks = [
            L2ScalabilityChecker(self.root, {}),
            TokenEconomyChecker(self.root, {}),
            SmartContractSecurityChecker(self.root, {}),
            PQCReadinessChecker(self.root, {})
        ]

    def run(self) -> Dict:
        logger.info(f"Starting Phase 3 Blockchain & Token Assessment | Root: {self.root}")
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
                        logger.warning(f"[{f.severity}] {f.category}: {f.message}")
                if any(f.severity == Severity.CRITICAL for f in r.findings):
                    has_crit = True
            except Exception as e:
                logger.error(f"Error in {nm}: {type(e).__name__}: {e}")
                results.append(asdict(Result(
                    nm, "FAIL", 0.0,
                    [Finding("CRITICAL", "PipelineError", f"{type(e).__name__}: {e}")]
                )))
                has_crit = True
        
        elapsed = time.time() - t0
        overall = sum(r["score"] for r in results) / len(results) if results else 0.0
        
        report = {
            "version": "3.0-final",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_score": round(overall, 3),
            "status": "PASS" if not has_crit else ("WARN" if any(r["status"] == "WARN" for r in results) else "FAIL"),
            "time_sec": round(elapsed, 2),
            "checks": results,
            "blockchain_readiness": "PRODUCTION_READY" if overall >= 0.8 else "DEVELOPMENT_PHASE",
            "next": (
                [f"Implement: {r['findings'][0]['recommendation']}" for r in results if r["status"] == "FAIL"] or
                [f"Optimize: {r['findings'][0]['recommendation']}" for r in results if r["status"] == "WARN"] or
                ["System fully assessed. Ready for deployment & monitoring phase."]
            )
        }
        
        rp = self.root / "phase3_blockchain_token_report.json"
        try:
            with open(rp, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Report saved: {rp}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
        
        if self.fail_on_critical and has_crit:
            logger.error("Critical finding detected - pipeline stopped")
            sys.exit(1)
        
        logger.info(f"Pipeline complete | Score: {overall:.2f} | Status: {report['status']} | Readiness: {report['blockchain_readiness']}")
        return report


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Phase 3 Blockchain & Token Economy Readiness Assessment")
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