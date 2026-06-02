from fastapi import APIRouter

router = APIRouter(tags=["Dashboard"])


@router.get("/stats")
async def dashboard_stats():
    return {
        "active_users": 12450,
        "active_modules": 15,
        "monthly_growth_percent": 24.5,
        "api_status": "healthy",
        "modules_online": [
            "weather",
            "accounting",
            "calendar",
            "gis",
            "auth",
            "farmer",
            "education",
            "psychology",
            "ecomining",
            "community",
            "games",
            "settings",
            "store",
            "library",
            "desktop",
        ],
    }
