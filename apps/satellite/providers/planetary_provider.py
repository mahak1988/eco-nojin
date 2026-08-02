"""Microsoft Planetary Computer STAC — free EO (optional pystac-client / rioxarray).

Phase 2: attempt real Sentinel-2 L2A NDVI from signed COG assets when
planetary-computer + rioxarray + rasterio are installed; otherwise metadata
cloud-weighted estimates so the chain never hard-fails.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from apps.satellite.providers.base import BBox, NDVIResult, SatelliteProvider, SatelliteSource

logger = logging.getLogger(__name__)


def _sign_item(item: Any) -> Any:
    try:
        import planetary_computer as pc

        return pc.sign(item)
    except Exception:
        return item


def _ndvi_from_item_raster(item: Any, bbox: BBox) -> tuple[float, float, float, float] | None:
    """Read B04 (red) + B08 (nir) COGs, compute NDVI stats for bbox."""
    try:
        import numpy as np
        import rioxarray  # noqa: F401
        import xarray as xr
    except ImportError:
        return None

    try:
        signed = _sign_item(item)
        assets = getattr(signed, "assets", {}) or {}
        red_href = None
        nir_href = None
        for key, asset in assets.items():
            k = key.lower()
            href = getattr(asset, "href", None) or (asset.get("href") if isinstance(asset, dict) else None)
            if not href:
                continue
            if k in ("b04", "red", "visual") or "b04" in k:
                if red_href is None and k != "visual":
                    red_href = href
            if k in ("b08", "nir") or "b08" in k:
                nir_href = href
        # Common S2 asset names on MPC
        if red_href is None and "B04" in assets:
            red_href = getattr(assets["B04"], "href", None)
        if nir_href is None and "B08" in assets:
            nir_href = getattr(assets["B08"], "href", None)
        if not red_href or not nir_href:
            return None

        red = rioxarray.open_rasterio(red_href, masked=True).squeeze(drop=True)
        nir = rioxarray.open_rasterio(nir_href, masked=True).squeeze(drop=True)
        # Clip to bbox (WGS84 → match CRS)
        try:
            red = red.rio.clip_box(
                minx=bbox.min_lng,
                miny=bbox.min_lat,
                maxx=bbox.max_lng,
                maxy=bbox.max_lat,
                crs="EPSG:4326",
            )
            nir = nir.rio.clip_box(
                minx=bbox.min_lng,
                miny=bbox.min_lat,
                maxx=bbox.max_lng,
                maxy=bbox.max_lat,
                crs="EPSG:4326",
            )
        except Exception:
            pass

        red_a = np.asarray(red.values, dtype=float)
        nir_a = np.asarray(nir.values, dtype=float)
        # Scale if digital numbers
        if np.nanmax(red_a) > 2.0:
            red_a = red_a / 10000.0
            nir_a = nir_a / 10000.0
        denom = nir_a + red_a
        with np.errstate(divide="ignore", invalid="ignore"):
            ndvi = (nir_a - red_a) / np.where(denom == 0, np.nan, denom)
        ndvi = ndvi[np.isfinite(ndvi)]
        if ndvi.size == 0:
            return None
        return (
            float(np.nanmean(ndvi)),
            float(np.nanmax(ndvi)),
            float(np.nanmin(ndvi)),
            float(np.nanstd(ndvi)) if ndvi.size > 1 else 0.05,
        )
    except Exception as e:
        logger.debug("MPC raster NDVI failed: %s", e)
        return None


class PlanetaryComputerProvider(SatelliteProvider):
    name = "microsoft-planetary-computer"
    STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

    @property
    def is_available(self) -> bool:
        try:
            import pystac_client  # noqa: F401

            return True
        except ImportError:
            return False

    def _open_catalog(self):
        import pystac_client

        try:
            import planetary_computer as pc

            return pystac_client.Client.open(
                self.STAC_URL,
                modifier=pc.sign_inplace,
            )
        except Exception:
            return pystac_client.Client.open(self.STAC_URL)

    async def get_availability(
        self, bbox: BBox, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        if not self.is_available:
            return [{"provider": self.name, "available": False, "reason": "pystac-client missing"}]
        try:
            catalog = self._open_catalog()
            search = catalog.search(
                collections=["sentinel-2-l2a"],
                bbox=bbox.to_list(),
                datetime=f"{start_date.isoformat()}/{end_date.isoformat()}",
                max_items=20,
            )
            items = list(search.items())
            return [
                {
                    "id": it.id,
                    "date": it.datetime.date().isoformat() if it.datetime else None,
                    "cloud_cover": (it.properties or {}).get("eo:cloud_cover"),
                    "source": "sentinel-2",
                    "provider": self.name,
                    "mode": "stac",
                }
                for it in items
            ]
        except Exception as e:
            logger.warning("MPC availability failed: %s", e)
            return [{"provider": self.name, "error": str(e)[:120]}]

    async def get_ndvi_timeseries(
        self,
        bbox: BBox,
        start_date: date,
        end_date: date,
        cloud_max: int = 20,
    ) -> list[NDVIResult]:
        """STAC search → prefer real raster NDVI; else cloud-weighted metadata estimate."""
        if not self.is_available:
            raise RuntimeError("Planetary Computer client not installed")

        catalog = self._open_catalog()
        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox.to_list(),
            datetime=f"{start_date.isoformat()}/{end_date.isoformat()}",
            query={"eo:cloud_cover": {"lt": cloud_max}},
            max_items=24,
        )
        items = list(search.items())
        if not items:
            return []

        results: list[NDVIResult] = []
        raster_ok = 0
        for it in items:
            d = it.datetime.date() if it.datetime else start_date
            cloud = float((it.properties or {}).get("eo:cloud_cover") or 0)
            stats = _ndvi_from_item_raster(it, bbox)
            if stats is not None:
                mean, mx, mn, std = stats
                raster_ok += 1
                mode = "raster"
            else:
                # Metadata fallback (free, no download) — cloud-weighted proxy
                mean = max(0.1, min(0.85, 0.55 - cloud / 200))
                mx = min(0.95, mean + 0.1)
                mn = max(0.0, mean - 0.1)
                std = 0.05
                mode = "metadata"

            results.append(
                NDVIResult(
                    date=d,
                    mean_ndvi=round(mean, 3),
                    max_ndvi=round(mx, 3),
                    min_ndvi=round(mn, 3),
                    std_ndvi=round(std, 3),
                    cloud_free_percentage=max(0.0, 100.0 - cloud),
                    source=SatelliteSource.SENTINEL2,
                    provider=f"{self.name}:{mode}",
                )
            )

        if raster_ok:
            logger.info("MPC NDVI: %s/%s scenes with raster stats", raster_ok, len(items))
        return sorted(results, key=lambda r: r.date)

    async def get_ndvi_image(
        self, bbox: BBox, target_date: date, cloud_max: int = 20
    ) -> NDVIResult:
        rows = await self.get_ndvi_timeseries(
            bbox, target_date - timedelta(days=7), target_date + timedelta(days=7), cloud_max
        )
        if not rows:
            raise RuntimeError("No MPC items")
        return min(rows, key=lambda r: abs((r.date - target_date).days))
