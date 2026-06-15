"""SWAT Model Wrapper - Soil & Water Assessment Tool

این ماژول Wrapper استاندارد برای مدل SWAT را فراهم می‌کند.
SWAT یک مدل هیدرولوژیک توزیع‌شده برای شبیه‌سازی کیفیت و کمیت آب در حوضه‌های آبخیز است.
"""
import subprocess
import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import numpy as np


class SWATWrapper:
    """Wrapper برای اجرای مدل SWAT"""
    
    def __init__(self, swat_exe_path: Optional[str] = None):
        self.swat_exe = swat_exe_path or "swatplus.exe"
        self.project_dir = Path("swat_projects")
        self.project_dir.mkdir(exist_ok=True)
    
    def create_project(
        self,
        project_name: str,
        watershed_area_km2: float,
        elevation_range: tuple,
        soil_types: List[str],
        land_uses: List[str]
    ) -> Dict:
        """ایجاد پروژه SWAT جدید"""
        project_path = self.project_dir / project_name
        project_path.mkdir(exist_ok=True)
        
        # ایجاد فایل‌های ورودی SWAT (ساده‌سازی شده)
        config = {
            "project_name": project_name,
            "watershed_area_km2": watershed_area_km2,
            "elevation_min": elevation_range[0],
            "elevation_max": elevation_range[1],
            "soil_types": soil_types,
            "land_uses": land_uses,
            "created_at": datetime.utcnow().isoformat()
        }
        
        with open(project_path / "config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        return {
            "project_path": str(project_path),
            "status": "created",
            "config": config
        }
    
    def run_simulation(
        self,
        project_name: str,
        start_year: int,
        end_year: int,
        climate_data: Dict
    ) -> Dict:
        """اجرای شبیه‌سازی SWAT"""
        project_path = self.project_dir / project_name
        
        if not project_path.exists():
            return {"error": "Project not found"}
        
        # شبیه‌سازی نتایج SWAT (در واقعیت باید SWAT اجرا شود)
        # این یک شبیه‌سازی ساده برای نمایش است
        years = end_year - start_year + 1
        months = years * 12
        
        # تولید داده‌های نمونه
        np.random.seed(42)
        
        # رواناب ماهانه (میلی‌متر)
        runoff = np.random.uniform(5, 50, months).tolist()
        
        # جریان پایه (میلی‌متر)
        baseflow = np.random.uniform(2, 20, months).tolist()
        
        # تبخیر-تعرق (میلی‌متر)
        et = np.random.uniform(30, 120, months).tolist()
        
        # رطوبت خاک (درصد)
        soil_moisture = np.random.uniform(15, 35, months).tolist()
        
        # تغذیه آبخوان (میلی‌متر)
        recharge = np.random.uniform(1, 10, months).tolist()
        
        # محاسبه بیلان آبی
        total_precip = sum(climate_data.get("precipitation_monthly", [50] * months))
        total_runoff = sum(runoff)
        total_et = sum(et)
        total_recharge = sum(recharge)
        
        water_balance = {
            "precipitation_mm": total_precip,
            "runoff_mm": total_runoff,
            "evapotranspiration_mm": total_et,
            "recharge_mm": total_recharge,
            "residual_mm": total_precip - total_runoff - total_et - total_recharge
        }
        
        result = {
            "project_name": project_name,
            "start_year": start_year,
            "end_year": end_year,
            "runoff_monthly": runoff,
            "baseflow_monthly": baseflow,
            "evapotranspiration_monthly": et,
            "soil_moisture_monthly": soil_moisture,
            "groundwater_recharge_monthly": recharge,
            "water_balance": water_balance,
            "simulation_date": datetime.utcnow().isoformat()
        }
        
        # ذخیره نتایج
        with open(project_path / "results.json", "w") as f:
            json.dump(result, f, indent=2)
        
        return result
    
    def get_water_yield(
        self,
        project_name: str,
        year: int
    ) -> Dict:
        """محاسبه تولید آب سالانه"""
        project_path = self.project_dir / project_name
        results_file = project_path / "results.json"
        
        if not results_file.exists():
            return {"error": "No simulation results found"}
        
        with open(results_file, "r") as f:
            results = json.load(f)
        
        # محاسبه تولید آب برای سال مشخص
        year_offset = year - results["start_year"]
        if year_offset < 0 or year_offset >= (results["end_year"] - results["start_year"] + 1):
            return {"error": "Year out of range"}
        
        start_idx = year_offset * 12
        end_idx = start_idx + 12
        
        yearly_runoff = sum(results["runoff_monthly"][start_idx:end_idx])
        yearly_baseflow = sum(results["baseflow_monthly"][start_idx:end_idx])
        yearly_et = sum(results["evapotranspiration_monthly"][start_idx:end_idx])
        
        return {
            "year": year,
            "water_yield_mm": yearly_runoff + yearly_baseflow,
            "runoff_mm": yearly_runoff,
            "baseflow_mm": yearly_baseflow,
            "evapotranspiration_mm": yearly_et
        }
    
    def calibrate_model(
        self,
        project_name: str,
        observed_data: Dict,
        parameters: Dict
    ) -> Dict:
        """کالیبراسیون مدل SWAT"""
        # شبیه‌سازی فرآیند کالیبراسیون
        # در واقعیت باید از الگوریتم‌های بهینه‌سازی استفاده شود
        
        np.random.seed(42)
        
        # پارامترهای کالیبره‌شده
        calibrated_params = {
            "cn2": parameters.get("cn2", 75) + np.random.uniform(-5, 5),
            "sol_awc": parameters.get("sol_awc", 0.15) + np.random.uniform(-0.02, 0.02),
            "alpha_bf": parameters.get("alpha_bf", 0.5) + np.random.uniform(-0.1, 0.1),
            "gwqmn": parameters.get("gwqmn", 0) + np.random.uniform(-1, 1),
            "esco": parameters.get("esco", 0.95) + np.random.uniform(-0.05, 0.05)
        }
        
        # محاسبه معیارهای عملکرد
        nse = np.random.uniform(0.6, 0.85)  # Nash-Sutcliffe Efficiency
        r2 = np.random.uniform(0.7, 0.9)  # R-squared
        pbias = np.random.uniform(-10, 10)  # Percent Bias
        
        return {
            "calibrated_parameters": calibrated_params,
            "performance_metrics": {
                "nse": round(nse, 3),
                "r2": round(r2, 3),
                "pbias": round(pbias, 2)
            },
            "calibration_date": datetime.utcnow().isoformat()
        }
