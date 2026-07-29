"""Copernicus Data Space — OData catalogue (auth optional)."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Optional

from apps.satellite.providers.base import BBox, NDVIResult, SatelliteProvider, SatelliteSource

logger = logging.getLogger(__name__)


class CopernicusProvider(SatelliteProvider):
    name = "copernicus-dataspace"
    ODATA_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1"
    AUTH_URL = (
        "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/"
        "protocol/openid-connect/token"
    )

    def __init__(self) -> None:
        self._token: Optional[str] = None

    @property
    def is_available(self) -> bool:
        try:
            from apps.shared_core.config import settings

            return bool(getattr(settings, "COPERNICUS_USERNAME", None))
        except Exception:
            return False

    async def _get_token(self) -> str:
        if self._token:
            return self._token
        import urllib.parse
        import urllib.request
        import json

        from apps.shared_core.config import settings

        data = urllib.parse.urlencode(
            {
                "grant_type": "password",
                "username": settings.COPERNICUS_USERNAME,
                "password": getattr(settings, "COPERNICUS_PASSWORD", "") or "",
                "client_id": "cdse-public",
            }
        ).encode()
        req = urllib.request.Request(self.AUTH_URL, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode())
        self._token = payload["access_token"]
        return self._token

    async def get_availability(
        self, bbox: BBox, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        if not self.is_available:
            return [{"source": "sentinel-2", "count": 0, "provider": self.name, "available": False}]
        try:
            import json
            import urllib.parse
            import urllib.request

            wkt = (
                f"POLYGON(({bbox.min_lng} {bbox.min_lat},{bbox.max_lng} {bbox.min_lat},"
                f"{bbox.max_lng} {bbox.max_lat},{bbox.min_lng} {bbox.max_lat},"
                f"{bbox.min_lng} {bbox.min_lat}))"
            )
            filter_str = (
                f"Collection/Name eq 'SENTINEL-2' "
                f"and OData.CSC.Intersects(area=geography'SRID=4326;{wkt}') "
                f"and ContentDate/Start gt {start_date.isoformat()}T00:00:00.000Z "
                f"and ContentDate/Start lt {end_date.isoformat()}T23:59:59.999Z"
            )
            qs = urllib.parse.urlencode(
                {"$filter": filter_str, "$top": "50", "$orderby": "ContentDate/Start desc"}
            )
            url = f"{self.ODATA_URL}/Products?{qs}"
            headers = {}
            try:
                headers["Authorization"] = f"Bearer {await self._get_token()}"
            except Exception:
                pass
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode())
            products = data.get("value") or []
            return [
                {
                    "id": p.get("Id"),
                    "name": p.get("Name"),
                    "date": (p.get("ContentDate") or {}).get("Start"),
                    "size_mb": (p.get("ContentLength") or 0) / 1e6,
                    "source": "sentinel-2",
                    "provider": self.name,
                }
                for p in products
            ]
        except Exception as e:
            logger.warning("Copernicus availability failed: %s", e)
            return [{"source": "sentinel-2", "error": str(e)[:120], "provider": self.name}]

    async def get_ndvi_timeseries(
        self,
        bbox: BBox,
        start_date: date,
        end_date: date,
        cloud_max: int = 20,
    ) -> list[NDVIResult]:
        # Catalogue-only in this build — processing via openEO is a follow-up
        raise RuntimeError(
            "Copernicus NDVI raster processing requires openEO pipeline; use GEE/MPC/synthetic"
        )

    async def get_ndvi_image(
        self, bbox: BBox, target_date: date, cloud_max: int = 20
    ) -> NDVIResult:
        raise RuntimeError("Copernicus get_ndvi_image not implemented without openEO")
