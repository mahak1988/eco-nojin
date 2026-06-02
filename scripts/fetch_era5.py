"""
دریافت داده‌های ERA5 - نسخه امن
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.logger import UnifiedLogger
from core.safety import SafeModuleLoader

logger = UnifiedLogger.get_logger('fetch_era5')


def fetch_era5_data(
    variable: str,
    year: int,
    output_path: Path
) -> bool:
    """
    دریافت داده‌های ERA5 از Copernicus
    
    Args:
        variable: نام متغیر (مثلاً 'temperature')
        year: سال
        output_path: مسیر ذخیره
    """
    try:
        # بارگذاری امن cdsapi
        import cdsapi
        
        client = cdsapi.Client()
        
        client.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': variable,
                'year': str(year),
                'month': [f'{m:02d}' for m in range(1, 13)],
                'day': [f'{d:02d}' for d in range(1, 32)],
                'time': ['00:00', '06:00', '12:00', '18:00'],
                'format': 'netcdf'
            },
            str(output_path)
        )
        
        logger.info(f"✅ Data saved to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Fetch failed: {e}")
        return False


if __name__ == "__main__":
    # تنظیمات از محیط
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    variable = os.getenv('ERA5_VARIABLE', '2m_temperature')
    year = int(os.getenv('ERA5_YEAR', '2023'))
    output = Path(os.getenv('ERA5_OUTPUT', './data/era5.nc'))
    
    success = fetch_era5_data(variable, year, output)
    sys.exit(0 if success else 1)
