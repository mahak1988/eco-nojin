"""Phase 5 — lightweight recommendation scoring engine.

Weighted feature scoring (no heavy ML deps). Acts as a transparent
"model" over dashboard/health/audit signals.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass
class FeatureWeights:
    inactive_users_ratio: float = 0.25
    audit_volume: float = 0.15
    settings_coverage: float = 0.10
    report_backlog: float = 0.15
    health_risk: float = 0.35


WEIGHTS = FeatureWeights()


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def score_system_state(
    *,
    user_count: int = 0,
    active_user_count: int = 0,
    total_settings: int = 0,
    total_audit_logs: int = 0,
    total_reports: int = 0,
    db_ok: bool = True,
    redis_ok: bool = True,
) -> dict[str, float]:
    """Compute normalized feature scores 0..1 (higher = more attention needed)."""
    inactive_ratio = 0.0
    if user_count > 0:
        inactive_ratio = _clamp(1.0 - (active_user_count / user_count))

    audit_score = _clamp(total_audit_logs / 500.0)
    settings_score = _clamp(1.0 - min(total_settings, 20) / 20.0)
    report_score = _clamp(total_reports / 50.0)
    health = 0.0
    if not db_ok:
        health += 0.7
    if not redis_ok:
        health += 0.3
    health = _clamp(health)

    composite = (
        WEIGHTS.inactive_users_ratio * inactive_ratio
        + WEIGHTS.audit_volume * audit_score
        + WEIGHTS.settings_coverage * settings_score
        + WEIGHTS.report_backlog * report_score
        + WEIGHTS.health_risk * health
    )

    return {
        "inactive_users_ratio": round(inactive_ratio, 3),
        "audit_volume": round(audit_score, 3),
        "settings_coverage": round(settings_score, 3),
        "report_backlog": round(report_score, 3),
        "health_risk": round(health, 3),
        "composite": round(composite, 3),
    }


def generate_scored_recommendations(features: dict[str, float]) -> list[dict[str, Any]]:
    """Map feature scores to actionable recommendations with confidence."""
    now = datetime.now(UTC).replace(tzinfo=None)
    recs: list[dict[str, Any]] = []

    rules = [
        (
            "inactive_users_ratio",
            0.4,
            {
                "id": "ml_inactive_users",
                "title": "فعال‌سازی کاربران غیرفعال",
                "description": "نسبت کاربران غیرفعال بالاست؛ کمپین فعال‌سازی یا پاکسازی حساب‌های راکد پیشنهاد می‌شود.",
                "category": "users",
                "priority": "high",
                "action": "review_inactive_users",
                "suggested_action": "review_inactive_users",
            },
        ),
        (
            "health_risk",
            0.3,
            {
                "id": "ml_health",
                "title": "بررسی سلامت زیرساخت",
                "description": "سیگنال سلامت پایگاه‌داده یا Redis ناسالم است.",
                "category": "infrastructure",
                "priority": "high",
                "action": "check_system_health",
                "suggested_action": "check_system_health",
            },
        ),
        (
            "audit_volume",
            0.5,
            {
                "id": "ml_audit",
                "title": "بازبینی لاگ‌های حسابرسی",
                "description": "حجم لاگ حسابرسی بالاست؛ الگوهای غیرعادی را بررسی کنید.",
                "category": "security",
                "priority": "medium",
                "action": "review_audit_logs",
                "suggested_action": "review_audit_logs",
            },
        ),
        (
            "settings_coverage",
            0.5,
            {
                "id": "ml_settings",
                "title": "تکمیل تنظیمات سیستم",
                "description": "پوشش تنظیمات سیستمی کم است؛ کلیدهای حیاتی را پیکربندی کنید.",
                "category": "configuration",
                "priority": "medium",
                "action": "complete_settings",
                "suggested_action": "complete_settings",
            },
        ),
        (
            "report_backlog",
            0.4,
            {
                "id": "ml_reports",
                "title": "پاکسازی گزارش‌های قدیمی",
                "description": "تعداد گزارش‌های سیستمی زیاد است؛ بایگانی یا حذف پیشنهاد می‌شود.",
                "category": "operations",
                "priority": "low",
                "action": "archive_reports",
                "suggested_action": "archive_reports",
            },
        ),
    ]

    for feature_key, threshold, template in rules:
        score = float(features.get(feature_key, 0))
        if score >= threshold:
            confidence = _clamp(0.55 + score * 0.4)
            if template["priority"] == "high" and score < 0.6:
                template = {**template, "priority": "medium"}
            recs.append(
                {
                    **template,
                    "confidence": round(confidence, 3),
                    "created_at": now,
                    "ml_score": score,
                    "model": "weighted_heuristic_v1",
                }
            )

    # Always emit at least one system-status recommendation
    if not recs:
        recs.append(
            {
                "id": "ml_stable",
                "title": "وضعیت پایدار",
                "description": "امتیاز ترکیبی سیستم در محدوده سالم است.",
                "category": "general",
                "priority": "low",
                "action": "monitor",
                "suggested_action": "monitor",
                "confidence": 0.9,
                "created_at": now,
                "ml_score": features.get("composite", 0),
                "model": "weighted_heuristic_v1",
            }
        )

    recs.sort(
        key=lambda r: (
            -{"high": 3, "medium": 2, "low": 1}.get(r["priority"], 0),
            -r.get("confidence", 0),
        )
    )
    return recs


async def build_ml_recommendations(admin_service) -> list[dict[str, Any]]:
    """End-to-end: pull live stats → score → recommendations."""
    try:
        dash = await admin_service.get_dashboard_summary()
        if hasattr(dash, "model_dump"):
            dash = dash.model_dump()
        elif not isinstance(dash, dict):
            dash = {}
    except Exception:
        dash = {}

    try:
        health = await admin_service.get_system_health()
        if not isinstance(health, dict):
            health = {}
    except Exception:
        health = {}

    db_status = str(health.get("database", "ok")).lower()
    redis_status = str(health.get("redis", "ok")).lower()

    features = score_system_state(
        user_count=int(dash.get("user_count") or 0),
        active_user_count=int(dash.get("active_user_count") or 0),
        total_settings=int(dash.get("total_settings") or 0),
        total_audit_logs=int(dash.get("total_audit_logs") or 0),
        total_reports=int(dash.get("total_reports") or 0),
        db_ok=db_status in ("ok", "healthy", "up"),
        redis_ok=redis_status in ("ok", "healthy", "up", "unavailable", "not_configured"),
    )
    return generate_scored_recommendations(features)
