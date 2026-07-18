"""
ماژول هشدارهای زیست‌محیطی Econojin — API endpoints
"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/alerts", tags=["🚨 Alerts"])

_alerts = [
    {"id": "alert-001", "category": "wildfire", "severity": "critical",
     "title": "آاای-سوزی جلهدامیال", "description": "اآاای-سوزی وامی دامد شکارک ℔ بامیاد انۨهاذه",
     "region": "کواهیامی راثدرا, اتان؆", "triggered_at": "2026-07-18T05:00:00Z",
     "acknowledged": False, "channels": ["in-app", "email"], "satellite": "VIIRS"},
    {"id": "alert-002", "category": "drought", "severity": "high",
     "title": "صوشه-شاهیه", "description": "کالیر 60% بارانخک اسیساان انروداه",
     "region": "سیرایلا و بیم؍وانیاه", "triggered_at": "2026-07-17T10:00:00Z",
     "acknowledged": False, "channels": ["in-app", "email"], "satellite": "SMAP"},
    {"id": "alert-003", "category": "flood", "severity": "high",
     "title": "هش�ار یول", "description": "اقعد اجامی آرو Y�معر ایزارک",
     "region": "رواطد ومعرر اتیاین", "triggered_at": "2026-07-17T08:00:00Z",
     "acknowledged": False, "channels": ["in-app", "sms"], "satellite": "GPM"},
    {"id": "alert-004", "category": "air-quality", "severity": "medium",
     "title": "اسویت۪g هنا", "description": "ای�(ایله AQI > 150 تیه تۇران",
     "region": "تۇران, اتانن", "triggered_at": "2026-07-16T12:00:00Z",
     "acknowledged": True, "channels": ["in-app"], "satellite": "Sentinel-5P"},
    {"id": "alert-005", "category": "deforestation", "severity": "medium",
     "title": "جلهدامیروانسی", "description": "قظُ -2 اقظ، ان۪aلن ادامیاد بالی 150 جلهد بومش کس انتوهن جلهدام مبانامیال",
     "region": "اجلهدامیامی عبیه, اتان", "triggered_at": "2026-07-16T06:00:00Z",
     "acknowledged": True, "channels": ["in-app", "email"], "satellite": "Landsat-8"},
]


@router.get("/")
async def list_alerts(
    severity: Optional[str] = Query(None, description="Filter: critical, high, medium, low"),
    acknowledged: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
):
    result = _alerts
    if severity:
        result = [a for a in result if a["severity"] == severity]
    if acknowledged is not None:
        result = [a for a in result if a["acknowledged"] == acknowledged]
    if category:
        result = [a for a in result if a["category"] == category]
    return {"alerts": result[:limit], "total": len(result)}


@router.get("/active")
async def get_active_alerts():
    active = [a for a in _alerts if not a["acknowledged"]]
    return {"alerts": active, "count": len(active)}


@router.get("/critical")
async def get_critical_alerts():
    critical = [a for a in _alerts if a["severity"] == "critical" and not a["acknowledged"]]
    return {"alerts": critical, "count": len(critical)}


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    for a in _alerts:
        if a["id"] == alert_id:
            a["acknowledged"] = True
            return {"status": "acknowledged", "alert_id": alert_id}
    return {"status": "not_found", "alert_id": alert_id}
