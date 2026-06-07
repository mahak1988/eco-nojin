from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from typing import Dict, Any
from fastapi import APIRouter, Body

router = APIRouter()


@router.post("/calculate/area", response_model=Dict[str, Any])
async def calculate_area(
    coordinates: list[list[float]] = Body(..., description="لیست مختصات [lon, lat]")
):
    if len(coordinates) < 3:
        return {"error": "حداقل ۳ نقطه نیاز است"}
    area = 0
    n = len(coordinates)
    for i in range(n):
        j = (i + 1) % n
        area += coordinates[i][0] * coordinates[j][1]
        area -= coordinates[j][0] * coordinates[i][1]
    return {
        "area_km2": abs(area) / 2 / 1_000_000,
        "perimeter_km": sum(
            (
                (coordinates[i][0] - coordinates[(i + 1) % n][0]) ** 2
                + (coordinates[i][1] - coordinates[(i + 1) % n][1]) ** 2
            )
            ** 0.5
            for i in range(n)
        )
        / 1000,
        "unit": "km",
    }


@router.get("/ndvi", response_model=Dict[str, Any])
async def get_ndvi(region: str = "خراسان"):
    return {"region": region, "avg_ndvi": 0.62, "status": "healthy", "last_updated": "2026-06-01"}


@router.get("/layers", response_model=Dict[str, Any])
async def map_layers():
    return {
        "base": {
            "name": "OpenStreetMap",
            "url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "attribution": "&copy; OpenStreetMap",
            "max_zoom": 19,
        },
        "satellite": {
            "name": "Esri World Imagery",
            "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            "attribution": "Esri",
            "max_zoom": 18,
        },
        "default_center": [36.3, 59.6],
        "default_zoom": 10,
    }
