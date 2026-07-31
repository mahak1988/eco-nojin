"""
Persistent dynamic thresholds for model monitors.

Storage: data/monitor_thresholds.json (project root).
Override keys: monitor_id -> { warning, critical, operator?, enabled? }
"""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_LOCK = threading.Lock()
_CACHE: dict[str, Any] | None = None

# Project root = parents[2] from apps/simulation/
_ROOT = Path(__file__).resolve().parents[2]
_PATH = _ROOT / "data" / "monitor_thresholds.json"

# Climate presets scale warning/critical relative to defaults (multipliers or offsets by op)
CLIMATE_PRESETS: dict[str, dict[str, Any]] = {
    "default": {"label_fa": "پیش‌فرض", "label_en": "Default", "scale": 1.0},
    "arid": {
        "label_fa": "خشک / نیمه‌خشک",
        "label_en": "Arid / semi-arid",
        # tighter water / NDVI; looser runoff
        "by_model": {
            "aquacrop": {"warning_mul": 1.05, "critical_mul": 1.0},  # for lt ops: higher bar = stricter? handled below
            "ndvi": {"warning_mul": 0.9, "critical_mul": 0.85},
            "scs": {"warning_mul": 0.7, "critical_mul": 0.75},
            "sensor": {"warning_mul": 0.85, "critical_mul": 0.9},
            "rothc": {"warning_mul": 1.0, "critical_mul": 1.0},
        },
    },
    "humid": {
        "label_fa": "مرطوب",
        "label_en": "Humid",
        "by_model": {
            "aquacrop": {"warning_mul": 0.95, "critical_mul": 0.95},
            "ndvi": {"warning_mul": 1.1, "critical_mul": 1.1},
            "scs": {"warning_mul": 1.3, "critical_mul": 1.25},
            "sensor": {"warning_mul": 1.1, "critical_mul": 1.05},
            "rothc": {"warning_mul": 1.0, "critical_mul": 1.0},
        },
    },
    "high_risk": {
        "label_fa": "ریسک بالا (سخت‌گیرانه)",
        "label_en": "High risk (strict)",
        "by_model": {
            "aquacrop": {"warning_mul": 1.1, "critical_mul": 1.1},
            "ndvi": {"warning_mul": 1.15, "critical_mul": 1.15},
            "scs": {"warning_mul": 0.8, "critical_mul": 0.85},
            "sensor": {"warning_mul": 1.1, "critical_mul": 1.1},
            "rothc": {"warning_mul": 1.2, "critical_mul": 1.2},
        },
    },
}


def _default_doc() -> dict[str, Any]:
    return {
        "version": 1,
        "preset": "default",
        "updated_at": None,
        "overrides": {},  # id -> {warning, critical, operator?, enabled?}
    }


def _load() -> dict[str, Any]:
    global _CACHE
    with _LOCK:
        if _CACHE is not None:
            return _CACHE
        if _PATH.is_file():
            try:
                data = json.loads(_PATH.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    data = _default_doc()
            except Exception:
                data = _default_doc()
        else:
            data = _default_doc()
        data.setdefault("overrides", {})
        data.setdefault("preset", "default")
        _CACHE = data
        return data


def _save(doc: dict[str, Any]) -> None:
    global _CACHE
    with _LOCK:
        _PATH.parent.mkdir(parents=True, exist_ok=True)
        doc["updated_at"] = datetime.now(UTC).isoformat()
        _PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        _CACHE = doc


def get_store() -> dict[str, Any]:
    return dict(_load())


def get_overrides() -> dict[str, dict[str, Any]]:
    return dict(_load().get("overrides") or {})


def set_overrides(overrides: dict[str, dict[str, Any]], *, merge: bool = True) -> dict[str, Any]:
    doc = _load()
    current = dict(doc.get("overrides") or {})
    if merge:
        for mid, body in overrides.items():
            if not isinstance(body, dict):
                continue
            prev = dict(current.get(mid) or {})
            for k in ("warning", "critical", "operator", "enabled"):
                if k in body and body[k] is not None:
                    prev[k] = body[k]
            current[mid] = prev
    else:
        current = {k: v for k, v in overrides.items() if isinstance(v, dict)}
    doc["overrides"] = current
    _save(doc)
    return get_store()


def set_preset(name: str) -> dict[str, Any]:
    if name not in CLIMATE_PRESETS:
        raise ValueError(f"unknown preset: {name}")
    doc = _load()
    doc["preset"] = name
    _save(doc)
    return get_store()


def reset_store() -> dict[str, Any]:
    doc = _default_doc()
    _save(doc)
    return doc


def apply_preset_to_value(
    model: str,
    operator: str,
    kind: str,  # warning | critical
    base: float,
    preset: str,
) -> float:
    """Scale threshold by climate preset. For 'lt' lower is worse → multiply scales the bar carefully."""
    cfg = CLIMATE_PRESETS.get(preset) or CLIMATE_PRESETS["default"]
    by = (cfg.get("by_model") or {}).get(model) or {}
    mul = float(by.get(f"{kind}_mul", cfg.get("scale", 1.0)))
    # lt: higher threshold = more lenient; mul>1 raises bar (more lenient for yield)
    # gt: higher threshold = more lenient; mul>1 raises bar
    return base * mul
