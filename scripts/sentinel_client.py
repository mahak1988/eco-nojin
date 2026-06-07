"""
Sentinel Satellite Data Client for Econojin
===========================================
Download Sentinel-2/1 data via STAC API or Earth Engine.
Open data, free access.

Reference: https://sentinel.esa.int/
"""

import warnings
from pathlib import Path
from typing import Dict, List, Optional

import odc.stac
import pystac_client
import xarray as xr


class SentinelClient:
    """
    Client for downloading Sentinel satellite data.

    Supports:
    - Sentinel-2: Optical imagery (10-60m resolution)
    - Sentinel-1: SAR imagery (5-20m resolution)

    Access methods:
    - STAC API (preferred): https://earth-search.aws.element84.com/v1
    - Google Earth Engine (alternative)
    """

    STAC_URL = "https://earth-search.aws.element84.com/v1"

    def __init__(self, use_earth_engine: bool = False):
        """
        Initialize Sentinel client.

        Parameters:
        -----------
        use_earth_engine : bool
            If True, use Google Earth Engine backend (requires authentication)
        """
        self.use_ee = use_earth_engine
        if not use_earth_engine:
            self.stac_client = pystac_client.Client.open(self.STAC_URL)

    def search_sentinel2(
        self,
        bbox: List[float],
        start_date: str,
        end_date: str,
        cloud_max: float = 20,
        bands: List[str] = None,
    ) -> pystac_client.ItemSearch:
        """
        Search Sentinel-2 items matching criteria.

        Parameters:
        -----------
        bbox : list
            [min_lon, min_lat, max_lon, max_lat]
        start_date, end_date : str
            ISO format dates
        cloud_max : float
            Maximum cloud cover percentage
        bands : list, optional
            Specific bands to download

        Returns:
        --------
        search : ItemSearch
            STAC search object
        """
        bands = bands or ["B02", "B03", "B04", "B08"]  # RGB + NIR

        search = self.stac_client.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=f"{start_date}/{end_date}",
            query={"eo:cloud_cover": {"lt": cloud_max}},
        )

        return search

    def download_ndvi(
        self, bbox: List[float], date: str, output_path: Path, cloud_max: float = 20
    ) -> Path:
        """
        Download and compute NDVI from Sentinel-2.

        NDVI = (NIR - Red) / (NIR + Red)
        """
        # Search for scene
        search = self.search_sentinel2(
            bbox=bbox,
            start_date=date,
            end_date=date,
            cloud_max=cloud_max,
            bands=["B04", "B08"],  # Red, NIR
        )

        items = list(search.items())
        if not items:
            raise ValueError(f"No Sentinel-2 scenes found for {date}")

        # Load data using odc.stac
        ds = odc.stac.load(
            items, bands=["B04", "B08"], bbox=bbox, resolution=10, crs="EPSG:4326"  # 10m resolution
        )

        # Calculate NDVI
        nir = ds["B08"]
        red = ds["B04"]
        ndvi = (nir - red) / (nir + red + 1e-10)  # Avoid division by zero
        ndvi = ndvi.clip(-1, 1)
        ndvi.attrs["long_name"] = "Normalized Difference Vegetation Index"

        # Save
        ndvi.to_netcdf(output_path)
        return output_path

    def get_timeseries_ndvi(
        self,
        bbox: List[float],
        start_date: str,
        end_date: str,
        point_lon: float,
        point_lat: float,
        cloud_max: float = 20,
    ) -> xr.DataArray:
        """
        Extract NDVI time series for a point location.

        Useful for vegetation monitoring and crop growth analysis.
        """
        search = self.search_sentinel2(
            bbox=bbox,
            start_date=start_date,
            end_date=end_date,
            cloud_max=cloud_max,
            bands=["B04", "B08"],
        )

        # Load and compute NDVI for each scene
        ndvi_series = []
        dates = []

        for item in search.items():
            try:
                ds = odc.stac.load([item], bands=["B04", "B08"], resolution=10, crs="EPSG:4326")

                nir = ds["B08"].sel(latitude=point_lat, longitude=point_lon, method="nearest")
                red = ds["B04"].sel(latitude=point_lat, longitude=point_lon, method="nearest")

                ndvi = (nir - red) / (nir + red + 1e-10)
                ndvi_series.append(ndvi.item())
                dates.append(item.datetime)

            except Exception as e:
                warnings.warn(f"Failed to process scene {item.id}: {e}")
                continue

        if not ndvi_series:
            raise ValueError("No valid NDVI values extracted")

        # Create time series
        return xr.DataArray(
            ndvi_series,
            coords={"time": dates},
            dims=["time"],
            attrs={"long_name": "NDVI time series", "location": f"{point_lat}, {point_lon}"},
        )
