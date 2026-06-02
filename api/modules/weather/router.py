from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/forecast")
async def get_forecast(location: str = Query("تهران", description="نام منطقه"), days: int = Query(7, ge=1, le=14)):
    return {
        "location": location,
        "days": days,
        "forecast": [{"day": f"روز {i+1}", "temp_c": 20 + i, "rain_chance": i * 5} for i in range(days)],
        "source": "offline_cached"
    }

@router.get("/alerts")
async def get_alerts(region: str = Query("خراسان", description="نام استان")):
    return {
        "region": region,
        "alerts": [
            {"type": "frost", "severity": "medium", "message": "احتمال یخبندان سهشب آینده"},
            {"type": "irrigation", "severity": "low", "message": "بهینهسازی زمان آبیاری فردا"}
        ],
        "last_updated": "2026-06-02T00:00:00Z"
    }
