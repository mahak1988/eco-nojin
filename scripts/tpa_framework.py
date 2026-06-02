#!/usr/bin/env python3
"""
Technical Project Assessment Framework (TPAF) v1.0
هدف: ارزیابی ساختاریافته پروژه بر اساس معماری، مقیاس‌پذیری، امنیت، عملکرد،
بلاکچین/ارز دیجیتال، هوش مصنوعی/ایجنت‌ها و کیفیت خدمات (QoS).
طراحی شده برای تیم‌های فنی داخلی با رویکرد ماژولار و قابل توسعه.
"""

import abc
import json
import logging
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

# پیکربندی لاگر: خروجی ساختاریافته و بدون نویز اضافی
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """ساختار داده برای خروجی هر ماژول ارزیابی."""
    module_name: str
    score: float  # 0.0 تا 1.0
    status: str   # "PASS", "WARNING", "CRITICAL", "N/A"
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)


class BaseEvaluator(abc.ABC):
    """پایه انتزاعی برای ماژول‌ها. رعایت اصل OCP برای توسعه آتی."""
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abc.abstractmethod
    def evaluate(self) -> EvaluationResult:
        """منطق اصلی ارزیابی هر ماژول."""
        pass

    def _calculate_weighted_score(self, criteria: Dict[str, bool]) -> float:
        """محاسبه امتیاز بر اساس نسبت معیارهای برقرار شده. جلوگیری از تقسیم بر صفر."""
        if not criteria:
            return 0.0
        return min(sum(criteria.values()) / len(criteria), 1.0)


class ScalabilityEvaluator(BaseEvaluator):
    def evaluate(self) -> EvaluationResult:
        criteria = {
            "horizontal_scaling": self.config.get("scaling", {}).get("horizontal", False),
            "stateless_design": self.config.get("scaling", {}).get("stateless", False),
            "load_balancing": self.config.get("scaling", {}).get("load_balancer", False),
            "caching_strategy": self.config.get("scaling", {}).get("caching", False),
        }
        score = self._calculate_weighted_score(criteria)
        status = "PASS" if score >= 0.75 else ("WARNING" if score >= 0.5 else "CRITICAL")
        findings = []
        if not criteria["horizontal_scaling"]: findings.append("پشتیبانی از مقیاس‌پذیری افقی تعریف نشده است.")
        if not criteria["stateless_design"]: findings.append("مدیریت وضعیت (State) ممکن است در مقیاس بالا گلوگاه ایجاد کند.")
        return EvaluationResult(
            module_name="Scalability", score=score, status=status, findings=findings,
            recommendations=["معماری Stateless برای سرویس‌ها", "پیاده‌سازی Redis/Memcached لایه‌ای", "اتوماسیون با Kubernetes HPA"],
            references=["K8s Gateway API", "Edge Computing Patterns 2026"]
        )


class SecurityEvaluator(BaseEvaluator):
    def evaluate(self) -> EvaluationResult:
        sec = self.config.get("security", {})
        criteria = {
            "zero_trust": sec.get("zero_trust", False),
            "secret_management": sec.get("secrets_manager", False),
            "sast_integration": sec.get("sast_in_ci", False),
            "dependency_scanning": sec.get("sbom_scanning", False),
        }
        score = self._calculate_weighted_score(criteria)
        status = "PASS" if score >= 0.8 else ("WARNING" if score >= 0.5 else "CRITICAL")
        findings = []
        if not criteria["zero_trust"]: findings.append("معماری Zero Trust پیاده‌سازی نشده است.")
        if not criteria["dependency_scanning"]: findings.append("فاقد SBOM و اسکن آسیب‌پذیری وابستگی‌ها.")
        return EvaluationResult(
            module_name="Security", score=score, status=status, findings=findings,
            recommendations=["پیاده‌سازی mTLS و سیاست‌های Least Privilege", "ادغام OWASP ZAP/Snyk در CI/CD", "آمادگی برای PQC (مقاوم در برابر کوانتوم)"],
            references=["NIST SP 800-207", "TRiSM Framework", "Post-Quantum Crypto Readiness"]
        )


class ArchitectureEvaluator(BaseEvaluator):
    def evaluate(self) -> EvaluationResult:
        arch = self.config.get("architecture", {})
        is_microservices = arch.get("style", "").lower() in ["microservices", "service-mesh"]
        has_api_gateway = arch.get("api_gateway", False)
        is_event_driven = arch.get("event_driven", False)
        criteria = {"microservices": is_microservices, "api_gateway": has_api_gateway, "event_driven": is_event_driven}
        score = self._calculate_weighted_score(criteria)
        status = "PASS" if score >= 0.66 else "WARNING"
        return EvaluationResult(
            module_name="Architecture", score=score, status=status,
            findings=[] if score > 0.5 else ["ساختار یکپارچه (Monolith) ممکن است توسعه و استقرار آتی را کند کند."],
            recommendations=["جداسازی دامنه‌ها (Domain-Driven Design)", "استفاده از Service Mesh برای مدیریت ترافیک", "پیاده‌سازی Composable Architecture"],
            references=["Microservices Patterns 2026", "Composable Architecture"]
        )


class PerformanceEvaluator(BaseEvaluator):
    def evaluate(self) -> EvaluationResult:
        perf = self.config.get("performance", {})
        criteria = {
            "caching": perf.get("caching_enabled", False),
            "db_optimization": perf.get("query_optimization", False),
            "async_processing": perf.get("async_workers", False),
            "cdn_usage": perf.get("cdn", False),
        }
        score = self._calculate_weighted_score(criteria)
        status = "PASS" if score >= 0.7 else "WARNING"
        return EvaluationResult(
            module_name="Performance", score=score, status=status,
            findings=["برای سنجش دقیق‌تر، استفاده از Locust/k6 و پروفایلینگ Async توصیه می‌شود."] if score < 0.8 else [],
            recommendations=["پیاده‌سازی Connection Pooling", "استفاده از Async I/O برای عملیات شبکه", "بهینه‌سازی ایندکس‌های دیتابیس و KVComp"],
            references=["KVComp Inference Optimization", "Non-blocking I/O Patterns"]
        )


class BlockchainCryptoEvaluator(BaseEvaluator):
    def evaluate(self) -> EvaluationResult:
        bc = self.config.get("blockchain", {})
        uses_l2 = bc.get("layer2_scaling", False)
        has_consensus_opt = bc.get("consensus_optimization", False)
        token_economy = bc.get("token_economy", False)
        # اگر بخش بلاکچین اصلاً تعریف نشده، وضعیت N/A برمی‌گردانیم
        if not bc:
            return EvaluationResult(module_name="Blockchain & Crypto", score=0.0, status="N/A", findings=["ماژول بلاکچین در پیکربندی تعریف نشده است."])
        
        criteria = {"l2_scaling": uses_l2, "consensus": has_consensus_opt, "economy": token_economy}
        score = self._calculate_weighted_score(criteria)
        status = "PASS" if score >= 0.6 else "WARNING"
        return EvaluationResult(
            module_name="Blockchain & Crypto", score=score, status=status,
            findings=["مقیاس‌پذیری لایه دوم یا بهینه‌سازی اجماع تعریف نشده است."] if status == "WARNING" else [],
            recommendations=["بررسی Rollups/Sharding برای TPS بالا", "پیاده‌سازی اقتصاد توکن برای Agentic Coordination", "استفاده از PQC برای امضای تراکنش‌ها"],
            references=["AGNT2 Protocol", "DeCoAgent Framework", "Post-Quantum Cryptography"]
        )


class AIAgentEvaluator(BaseEvaluator):
    def evaluate(self) -> EvaluationResult:
        ai = self.config.get("ai_agents", {})
        has_orchestration = ai.get("orchestration", False)
        has_memory = ai.get("shared_memory_world_model", False)
        has_safety = ai.get("agent_safety_trism", False)
        criteria = {"orchestration": has_orchestration, "memory": has_memory, "safety": has_safety}
        score = self._calculate_weighted_score(criteria)
        status = "PASS" if score >= 0.66 else "WARNING"
        return EvaluationResult(
            module_name="AI & Agents", score=score, status=status,
            findings=["سیستم فدراسیونی یا Edge Execution برای کاهش تأخیر توصیه می‌شود."] if not has_orchestration else [],
            recommendations=["پیاده‌سازی Multi-Agent Orchestration", "استفاده از TRiSM برای مدیریت ریسک ایجنت‌ها", "جداسازی Execution Rings برای امنیت"],
            references=["Agent Governance Toolkit", "TRiSM Framework", "Edge AI 2026"]
        )


class QoSEvaluator(BaseEvaluator):
    def evaluate(self) -> EvaluationResult:
        qos = self.config.get("qos", {})
        has_observability = qos.get("observability", False)
        has_sla_monitoring = qos.get("sla_monitoring", False)
        has_feedback_loop = qos.get("user_feedback_loop", False)
        criteria = {"observability": has_observability, "sla": has_sla_monitoring, "feedback": has_feedback_loop}
        score = self._calculate_weighted_score(criteria)
        status = "PASS" if score >= 0.7 else "WARNING"
        return EvaluationResult(
            module_name="Quality of Service (QoS)", score=score, status=status,
            findings=["پیاده‌سازی OpenTelemetry برای Tracing و Metrics ضروری است."] if not has_observability else [],
            recommendations=["تعریف SLI/SLO/SLA شفاف", "ادغام APM و Log Aggregation", "پیاده‌سازی Circuit Breaker و Retry Policy"],
            references=["SRE Google Handbook", "Agentic Observability Standards"]
        )


class ProjectAnalyzer:
    """هماهنگ‌کننده اصلی (Orchestrator). اجرای موازی، مدیریت خطا و تولید گزارش."""
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.evaluators: List[BaseEvaluator] = []
        self._load_config()
        self._init_evaluators()

    def _load_config(self) -> None:
        """بارگذاری و اعتبارسنجی ایمن فایل پیکربندی."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"فایل پیکربندی یافت نشد: {self.config_path}")
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            logger.info("فایل پیکربندی با موفقیت بارگذاری شد.")
        except json.JSONDecodeError as e:
            logger.error(f"فرمت JSON نامعتبر است: {e}")
            sys.exit(1)

    def _init_evaluators(self) -> None:
        """ثبت ماژول‌های ارزیابی (Factory Pattern)."""
        self.evaluators = [
            ScalabilityEvaluator(self.config),
            SecurityEvaluator(self.config),
            ArchitectureEvaluator(self.config),
            PerformanceEvaluator(self.config),
            BlockchainCryptoEvaluator(self.config),
            AIAgentEvaluator(self.config),
            QoSEvaluator(self.config),
        ]

    def run(self) -> Dict[str, Any]:
        """اجرای موازی ارزیابی‌ها و تولید گزارش نهایی."""
        logger.info("شروع فرآیند ارزیابی فنی...")
        results: List[EvaluationResult] = []

        # اجرای همزمان برای بهبود پرفورمنس (I/O Bound + Light CPU)
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_module = {
                executor.submit(evaluator.evaluate): evaluator.__class__.__name__
                for evaluator in self.evaluators
            }
            for future in as_completed(future_to_module):
                module_name = future_to_module[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # جلوگیری از Silent Failure: خطا لاگ شده و نتیجه CRITICAL ثبت می‌شود
                    logger.error(f"خطا در ماژول {module_name}: {e}")
                    results.append(EvaluationResult(
                        module_name=module_name, score=0.0, status="CRITICAL",
                        findings=[f"خطای اجرا: {e}"], recommendations=["بررسی لاگ‌ها و رفع خطای ماژول"]
                    ))

        return self._generate_report(results)

    def _generate_report(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """تولید گزارش ساختاریافته و قابل ماشین‌خوانی."""
        overall_score = sum(r.score for r in results) / len(results) if results else 0.0
        report = {
            "assessment_metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "framework_version": "1.0.0",
                "target_audience": "Internal Technical Team"
            },
            "overall_health": {
                "score": round(overall_score, 2),
                "status": "HEALTHY" if overall_score >= 0.7 else ("AT_RISK" if overall_score >= 0.5 else "CRITICAL")
            },
            "module_results": [asdict(r) for r in results],
            "next_steps": self._generate_next_steps(results)
        }
        return report

    def _generate_next_steps(self, results: List[EvaluationResult]) -> List[str]:
        steps = []
        critical_modules = [r.module_name for r in results if r.status == "CRITICAL"]
        if critical_modules:
            steps.append(f"🔴 اولویت اول: رفع وضعیت بحرانی در ماژول‌های {critical_modules}")
        warning_modules = [r.module_name for r in results if r.status == "WARNING"]
        if warning_modules:
            steps.append(f"🟡 بهبود وضعیت هشدار در ماژول‌های {warning_modules}")
        if not steps:
            steps.append("✅ معماری فعلی با استانداردهای ۲۰۲۶ همخوانی دارد. بر روی بهینه‌سازی پیوسته و Shift-Left Security تمرکز کنید.")
        return steps


def main():
    config_file = Path("project_assessment_config.json")
    try:
        analyzer = ProjectAnalyzer(config_file)
        report = analyzer.run()
        report_path = Path("technical_assessment_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"گزارش نهایی ذخیره شد: {report_path}")
        logger.info(f"امتیاز کلی: {report['overall_health']['score']} | وضعیت: {report['overall_health']['status']}")
    except Exception as e:
        logger.error(f"شروع تحلیل ناموفق بود: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()