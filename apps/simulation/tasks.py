"""Celery tasks — AquaCrop / RothC stubs + PDF/CSV export."""

from __future__ import annotations

import csv
import io
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps.shared_core.celery_app import celery_app

logger = logging.getLogger(__name__)
EXPORT_DIR = Path("artifacts/simulation_exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _run_aquacrop_sync(params: dict[str, Any]) -> dict[str, Any]:
    """Lightweight deterministic AquaCrop-like water balance stub."""
    area_ha = float(params.get("area_ha", 1.0))
    et0 = float(params.get("et0_mm_day", 4.0))
    kc = float(params.get("kc", 1.0))
    days = int(params.get("days", 30))
    rain = float(params.get("rain_mm_total", 20.0))
    etc = et0 * kc * days
    irrigation_need = max(0.0, etc - rain)
    yield_index = max(0.2, min(1.0, 1 - irrigation_need / (etc + 1e-6) * 0.5))
    return {
        "model": "aquacrop_stub",
        "area_ha": area_ha,
        "etc_mm": round(etc, 2),
        "irrigation_need_mm": round(irrigation_need, 2),
        "irrigation_m3": round(irrigation_need * 10 * area_ha, 1),
        "yield_index": round(yield_index, 3),
        "days": days,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }


def _run_rothc_sync(params: dict[str, Any]) -> dict[str, Any]:
    """RothC-like SOC stock change stub."""
    soc0 = float(params.get("soc_t_ha", 40.0))
    clay = float(params.get("clay_pct", 25.0))
    temp = float(params.get("temp_c", 18.0))
    years = int(params.get("years", 10))
    # simplified decay + input
    k = 0.02 * (1 + (temp - 10) / 40) * (1 - clay / 200)
    inputs = float(params.get("c_input_t_ha_y", 1.5))
    soc = soc0
    series = []
    for y in range(years + 1):
        series.append({"year": y, "soc_t_ha": round(soc, 2)})
        soc = soc * (1 - k) + inputs
    return {
        "model": "rothc_stub",
        "soc_initial": soc0,
        "soc_final": series[-1]["soc_t_ha"],
        "delta": round(series[-1]["soc_t_ha"] - soc0, 2),
        "series": series,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _write_pdf_stub(path: Path, title: str, body: dict[str, Any]) -> None:
    """Minimal PDF without heavy deps (PDF 1.1 text)."""
    text = f"{title}\n\n{json.dumps(body, indent=2)}"
    # Escape for PDF literal
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    lines = safe.split("\n")[:80]
    content_lines = ["BT /F1 10 Tf 40 750 Td"]
    for i, line in enumerate(lines):
        if i == 0:
            content_lines.append(f"({line[:100]}) Tj")
        else:
            content_lines.append(f"0 -12 Td ({line[:100]}) Tj")
    content_lines.append("ET")
    stream = "\n".join(content_lines)
    objects = []
    objects.append("1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n")
    objects.append("2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n")
    objects.append(
        "3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n"
    )
    objects.append(f"4 0 obj<< /Length {len(stream)} >>stream\n{stream}\nendstream\nendobj\n")
    objects.append("5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n")
    out = io.BytesIO()
    out.write(b"%PDF-1.1\n")
    offsets = [0]
    for obj in objects:
        offsets.append(out.tell())
        out.write(obj.encode("latin-1", errors="replace"))
    xref_pos = out.tell()
    out.write(f"xref\n0 {len(offsets)}\n".encode())
    out.write(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.write(f"{off:010d} 00000 n \n".encode())
    out.write(
        f"trailer<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    )
    path.write_bytes(out.getvalue())


@celery_app.task(name="simulation.run_aquacrop", bind=True)
def run_aquacrop(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
    params = params or {}
    result = _run_aquacrop_sync(params)
    run_id = self.request.id or datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    csv_path = EXPORT_DIR / f"aquacrop_{run_id}.csv"
    pdf_path = EXPORT_DIR / f"aquacrop_{run_id}.pdf"
    _write_csv(
        csv_path,
        [
            {
                "metric": k,
                "value": v,
            }
            for k, v in result.items()
            if not isinstance(v, (list, dict))
        ],
    )
    _write_pdf_stub(pdf_path, "AquaCrop Simulation Report", result)
    result["export_csv"] = str(csv_path)
    result["export_pdf"] = str(pdf_path)
    result["task_id"] = run_id
    logger.info("AquaCrop task done %s", run_id)
    return result


@celery_app.task(name="simulation.run_rothc", bind=True)
def run_rothc(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
    params = params or {}
    result = _run_rothc_sync(params)
    run_id = self.request.id or datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    csv_path = EXPORT_DIR / f"rothc_{run_id}.csv"
    pdf_path = EXPORT_DIR / f"rothc_{run_id}.pdf"
    series = result.get("series") or []
    _write_csv(csv_path, series if series else [{"soc": result.get("soc_final")}])
    _write_pdf_stub(pdf_path, "RothC Simulation Report", {k: v for k, v in result.items() if k != "series"})
    result["export_csv"] = str(csv_path)
    result["export_pdf"] = str(pdf_path)
    result["task_id"] = run_id
    return result


def run_aquacrop_local(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Sync fallback when Celery/Redis unavailable."""
    result = _run_aquacrop_sync(params or {})
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    pdf_path = EXPORT_DIR / f"aquacrop_{run_id}.pdf"
    csv_path = EXPORT_DIR / f"aquacrop_{run_id}.csv"
    _write_csv(csv_path, [{"metric": k, "value": v} for k, v in result.items() if not isinstance(v, (list, dict))])
    _write_pdf_stub(pdf_path, "AquaCrop Simulation Report", result)
    result["export_csv"] = str(csv_path)
    result["export_pdf"] = str(pdf_path)
    result["task_id"] = run_id
    result["mode"] = "sync_local"
    return result


def run_rothc_local(params: dict[str, Any] | None = None) -> dict[str, Any]:
    result = _run_rothc_sync(params or {})
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    pdf_path = EXPORT_DIR / f"rothc_{run_id}.pdf"
    csv_path = EXPORT_DIR / f"rothc_{run_id}.csv"
    _write_csv(csv_path, result.get("series") or [])
    _write_pdf_stub(pdf_path, "RothC Simulation Report", {k: v for k, v in result.items() if k != "series"})
    result["export_csv"] = str(csv_path)
    result["export_pdf"] = str(pdf_path)
    result["task_id"] = run_id
    result["mode"] = "sync_local"
    return result
