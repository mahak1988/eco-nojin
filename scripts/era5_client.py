"""
ERA5 Climate Data Client for Econojin
=====================================
Download and process ERA5 reanalysis data from CDS API.
Open data, free for research and development.

Reference: https://cds.climate.copernicus.eu/
"""

import cdsapi
import xarray as xr
import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict
import warnings


class ERA5Client:
    """
    Client for downloading ERA5 climate reanalysis data.

    Variables available:
    - 2m temperature, min/max
    - Precipitation
    - Surface radiation
    - Wind speed
    - Evaporation
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ERA5 client.

        Parameters:
        -----------
        api_key : str, optional
            CDS API key. If None, reads from environment variable CDSAPI_KEY.
        """
        self.client = cdsapi.Client(url='https://cds.climate.copernicus.eu/api')

    def download_monthly(
        self,
        variables: List[str],
        bbox: List[float],  # [north, west, south, east]
        start_date: str,
        end_date: str,
        output_path: Path
    ) -> Path:
        """
        Download monthly ERA5 data for a region.

        Parameters:
        -----------
        variables : list of str
            Variable names (see CDS catalog)
        bbox : list of float
            Bounding box [N, W, S, E]
        start_date, end_date : str
            Date range 'YYYY-MM-DD'
        output_path : Path
            Output file path

        Returns:
        --------
        output_path : Path
            Path to downloaded NetCDF file
        """
        request = {
            'product_type': 'monthly_averaged_reanalysis',
            'variable': variables,
            'year': self._date_range_to_years(start_date, end_date),
            'month': self._all_months(),
            'time': '00:00',
            'area': bbox,
            'format': 'netcdf',
        }

        self.client.retrieve('reanalysis-era5-single-levels-monthly-means',
                           request, output_path)

        return output_path

    def download_hourly(
        self,
        variables: List[str],
        bbox: List[float],
        start_date: str,
        end_date: str,
        output_path: Path
    ) -> Path:
        """Download hourly ERA5 data (larger files, use with caution)"""
        request = {
            'product_type': 'reanalysis',
            'variable': variables,
            'year': self._date_range_to_years(start_date, end_date),
            'month': self._all_months(),
            'day': self._all_days(),
            'time': self._all_hours(),
            'area': bbox,
            'format': 'netcdf',
        }

        self.client.retrieve('reanalysis-era5-single-levels',
                           request, output_path)

        return output_path

    def process_for_model(
        self,
        file_path: Path,
        target_variables: Dict[str, str],
        target_crs: str = 'EPSG:4326'
    ) -> xr.Dataset:
        """
        Process downloaded ERA5 data for Econojin models.

        Parameters:
        -----------
        file_path : Path
            Downloaded NetCDF file
        target_variables : dict
            Mapping: model_name -> era5_variable_name
        target_crs : str
            Target coordinate reference system

        Returns:
        --------
        processed : xr.Dataset
            Processed data ready for modeling
        """
        ds = xr.open_dataset(file_path)

        # Rename variables to model conventions
        rename_map = {v: k for k, v in target_variables.items()}
        ds = ds.rename(rename_map)

        # Convert units if needed
        if 'precip' in ds:
            # ERA5 precip: m -> mm
            ds['precip'] = ds['precip'] * 1000

        if 'temp' in ds:
            # ERA5 temp: K -> °C
            ds['temp'] = ds['temp'] - 273.15

        # Calculate derived variables
        if 'et0' in target_variables and 'et0' not in ds:
            ds['et0'] = self._calculate_et0(ds)

        # Reproject if needed
        if ds.rio.crs != target_crs and GIS_AVAILABLE:
            ds = ds.rio.reproject(target_crs)

        return ds

    def _calculate_et0(self, ds: xr.Dataset) -> xr.DataArray:
        """Calculate FAO-56 Penman-Monteith ET0 from ERA5 variables"""
        # Simplified implementation - full version needs radiation, humidity, wind
        # For now, use temperature-based Hargreaves method

        t_mean = ds['t2m'] - 273.15  # K to °C
        t_max = ds.get('tmax', t_mean + 5)
        t_min = ds.get('tmin', t_mean - 5)

        # Extraterrestrial radiation (simplified by latitude)
        ra = 40  # MJ/m²/day average

        # Hargreaves equation
        et0 = 0.0023 * ra * (t_mean + 17.8) * (t_max - t_min) ** 0.5

        return et0.clip(0)

    @staticmethod
    def _date_range_to_years(start: str, end: str) -> List[str]:
        """Convert date range to list of years"""
        start_year = pd.to_datetime(start).year
        end_year = pd.to_datetime(end).year
        return [str(y) for y in range(start_year, end_year + 1)]

    @staticmethod
    def _all_months() -> List[str]:
        return [f'{m:02d}' for m in range(1, 13)]

    @staticmethod
    def _all_days() -> List[str]:
        return [f'{d:02d}' for d in range(1, 32)]

    @staticmethod
    def _all_hours() -> List[str]:
        return [f'{h:02d}:00' for h in range(0, 24)]
