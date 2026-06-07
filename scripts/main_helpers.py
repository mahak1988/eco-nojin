"""
توابع کمکی برای main.py
جداسازی برای جلوگیری از circular imports
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Any, Dict, List

import structlog

from api.database import async_session_maker
from api.repository import AnalysisRepository
from api.schemas import AnalysisRequest

logger = structlog.get_logger()


# موقعیت‌های پیش‌فرض مناطق
REGION_COORDINATES = {
    "خراسان": {"lat": 36.2972, "lon": 59.6067},
    "مشهد": {"lat": 36.2972, "lon": 59.6067},
    "گرگان": {"lat": 36.8389, "lon": 54.4347},
    "تهران": {"lat": 35.6892, "lon": 51.3890},
    "اصفهان": {"lat": 32.6546, "lon": 51.6680},
    "شیراز": {"lat": 29.5916, "lon": 52.5837},
}


def extract_metrics_from_response(tasks: Dict[str, Any]) -> Dict[str, Any]:
    """استخراج شاخص‌های کلیدی از نتیجه workflow با regex"""
    metrics = {}
    tools_used = set()

    for task_id, task in tasks.items():
        output = task.get("output", "")
        task_tools = task.get("tools_used", [])
        tools_used.update(task_tools)

        # استخراج NDVI
        ndvi_match = re.search(r"NDVI[^\d]*(\d+\.\d+)", output)
        if ndvi_match:
            metrics["ndvi_avg"] = float(ndvi_match.group(1))

        health_match = re.search(r"وضعیت\s+(\S+)", output)
        if health_match:
            metrics["ndvi_health"] = health_match.group(1)

        # استخراج فرسایش
        erosion_match = re.search(r"فرسایش خاک[^\d]*(\d+\.\d+)", output)
        if erosion_match:
            metrics["erosion_rate"] = float(erosion_match.group(1))

        severity_match = re.search(r"فرسایش خاک[^\(]*\(([^)]+)\)", output)
        if severity_match:
            metrics["erosion_severity"] = severity_match.group(1)

        # استخراج بارش
        rain_match = re.search(r"بارش[^\d]*(\d+\.\d+)", output)
        if rain_match:
            metrics["rainfall_30d"] = float(rain_match.group(1))

        # استخراج عملکرد
        yield_match = re.search(r"عملکرد[^\d]*(\d+\.\d+)", output)
        if yield_match:
            metrics["predicted_yield"] = float(yield_match.group(1))

        # استخراج نیاز آبیاری
        irr_match = re.search(r"آبیاری[^\d]*(\d+)", output)
        if irr_match:
            metrics["irrigation_need"] = float(irr_match.group(1))

    metrics["tools_used"] = list(tools_used)
    return metrics


async def extract_and_save_analysis(
    session_id: str,
    request: AnalysisRequest,
    result: Dict[str, Any],
) -> None:
    """استخراج و ذخیره نتیجه تحلیل در دیتابیس"""
    try:
        metrics = extract_metrics_from_response(result["tasks"])

        # موقعیت منطقه
        region_coords = REGION_COORDINATES.get(
            request.region.value, {"lat": 35.6892, "lon": 51.3890}
        )

        save_data = {
            "session_id": session_id,
            "region": request.region.value,
            "query": request.query,
            "latitude": region_coords["lat"],
            "longitude": region_coords["lon"],
            "quality_score": result["review_summary"].get("quality_score", 0.0),
            "execution_time_ms": result.get("total_execution_time_ms", 0.0),
            "full_response": result.get("final_response", ""),
            **metrics,
        }

        async with async_session_maker() as session:
            repo = AnalysisRepository(session)
            await repo.save_analysis(save_data)
            await session.commit()

        logger.info(
            "analysis_saved",
            session_id=session_id,
            region=request.region.value,
        )

    except Exception as e:
        logger.error(
            "extract_and_save_failed",
            error=str(e),
            error_type=type(e).__name__,
            session_id=session_id,
        )
        raise
