"""
CHIRPS Precipitation Data Client for Econojin
=============================================
Download CHIRPS rainfall data from UCSB server.
Open data, no API key required.

Reference: https://www.chc.ucsb.edu/data/chirps
"""

import warnings
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import requests
import xarray as xr


class CHIRPSClient:
    """
    Client for downloading CHIRPS precipitation data.

    Resolution: 0.05° (~5 km)
    Temporal: Daily, monthly, pentadal
    Coverage: 50°S-50°N, 1981-present
    """

    BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS-2.0"

    def __init__(self):
        self.session = requests.Session()

    def download_daily(
        self,
        bbox: Tuple[float, float, float, float],  # [min_lat, min_lon, max_lat, max_lon]
        start_date: str,
        end_date: str,
        output_path: Path,
    ) -> Path:
        """
        Download daily CHIRPS data.

        Note: Daily downloads are large. Consider monthly for long periods.
        """
        # CHIRPS daily files are organized by year
        years = self._get_year_range(start_date, end_date)

        all_files = []
        for year in years:
            url = f"{self.BASE_URL}/global_daily/netcdf/p05/chirps-v2.0.{year}.days_p05.nc"
            temp_file = output_path.parent / f"chirps_{year}.nc"

            response = self.session.get(url, stream=True)
            response.raise_for_status()

            with open(temp_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            all_files.append(temp_file)

        # Merge and clip to bbox
        merged = self._merge_and_clip(all_files, bbox, start_date, end_date)
        merged.to_netcdf(output_path)

        # Cleanup temp files
        for f in all_files:
            f.unlink()

        return output_path

    def download_monthly(
        self,
        bbox: Tuple[float, float, float, float],
        start_date: str,
        end_date: str,
        output_path: Path,
    ) -> Path:
        """Download monthly CHIRPS data (recommended for most applications)"""
        years = self._get_year_range(start_date, end_date)

        all_files = []
        for year in years:
            url = f"{self.BASE_URL}/global_monthly/netcdf/p05/chirps-v2.0.{year}.months_p05.nc"
            temp_file = output_path.parent / f"chirps_monthly_{year}.nc"

            response = self.session.get(url, stream=True)
            response.raise_for_status()

            with open(temp_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            all_files.append(temp_file)

        # Merge and clip
        merged = self._merge_and_clip(all_files, bbox, start_date, end_date)
        merged.to_netcdf(output_path)

        for f in all_files:
            f.unlink()

        return output_path

    def _merge_and_clip(
        self,
        files: List[Path],
        bbox: Tuple[float, float, float, float],
        start_date: str,
        end_date: str,
    ) -> xr.Dataset:
        """Merge multiple files and clip to spatial-temporal bounds"""
        import pandas as pd

        # Open and concatenate
        datasets = [xr.open_dataset(f) for f in files]
        merged = xr.concat(datasets, dim="time")

        # Clip time
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        merged = merged.sel(time=slice(start, end))

        # Clip spatial (if coordinates available)
        if "latitude" in merged.coords and "longitude" in merged.coords:
            merged = merged.sel(
                latitude=slice(bbox[2], bbox[0]),  # Note: lat goes from N to S
                longitude=slice(bbox[1], bbox[3]),
            )

        return merged

    @staticmethod
    def _get_year_range(start: str, end: str) -> List[str]:
        """Extract years from date range"""
        import pandas as pd

        start_year = pd.to_datetime(start).year
        end_year = pd.to_datetime(end).year
        return [str(y) for y in range(start_year, end_year + 1)]
