"""Hydrology Service - Integrated Hydrological Modeling"""
from typing import Dict, List, Optional
from datetime import datetime
import uuid
from .models.hydrology_models import (
    Watershed,
    HydrologicalScenario,
    SimulationResult,
    ModelType,
    SimulationStatus
)
from .repositories.hydrology_repository import HydrologyRepository
from api.services.hydrology.swat_wrapper import SWATWrapper
from api.services.hydrology.weap_wrapper import WEAPWrapper


class HydrologyService:
    """سرویس مدل‌سازی هیدرولوژیک یکپارچه"""
    
    def __init__(self, repository: HydrologyRepository):
        self.repo = repository
        self.swat = SWATWrapper()
        self.weap = WEAPWrapper()
    
    async def create_watershed(
        self,
        watershed_id: str,
        name: str,
        area_km2: float,
        outlet_lat: float,
        outlet_lon: float,
        pilot_site: Optional[str] = None
    ) -> Watershed:
        """ایجاد حوضه آبخیز جدید"""
        watershed = Watershed(
            watershed_id=watershed_id,
            name=name,
            area_km2=area_km2,
            outlet_lat=outlet_lat,
            outlet_lon=outlet_lon,
            pilot_site=pilot_site
        )
        
        await self.repo.save_watershed(watershed)
        return watershed
    
    async def run_swat_simulation(
        self,
        watershed_id: str,
        scenario_name: str,
        start_year: int,
        end_year: int,
        climate_data: Dict
    ) -> Dict:
        """اجرای شبیه‌سازی SWAT"""
        # ایجاد سناریو
        scenario_id = str(uuid.uuid4())
        scenario = HydrologicalScenario(
            scenario_id=scenario_id,
            name=scenario_name,
            description=f"SWAT simulation for {start_year}-{end_year}",
            model_type=ModelType.SWAT,
            watershed_id=watershed_id,
            start_date=datetime(start_year, 1, 1),
            end_date=datetime(end_year, 12, 31),
            parameters=climate_data,
            status=SimulationStatus.RUNNING
        )
        
        await self.repo.save_scenario(scenario)
        
        # اجرای SWAT
        project_name = f"swat_{watershed_id}_{scenario_id[:8]}"
        swat_result = self.swat.run_simulation(
            project_name=project_name,
            start_year=start_year,
            end_year=end_year,
            climate_data=climate_data
        )
        
        if "error" in swat_result:
            scenario.status = SimulationStatus.FAILED
            await self.repo.save_scenario(scenario)
            return swat_result
        
        # ذخیره نتایج
        result = SimulationResult(
            result_id=str(uuid.uuid4()),
            scenario_id=scenario_id,
            model_type=ModelType.SWAT,
            watershed_id=watershed_id,
            start_date=datetime(start_year, 1, 1),
            end_date=datetime(end_year, 12, 31),
            runoff_monthly=swat_result["runoff_monthly"],
            baseflow_monthly=swat_result["baseflow_monthly"],
            evapotranspiration_monthly=swat_result["evapotranspiration_monthly"],
            soil_moisture_monthly=swat_result["soil_moisture_monthly"],
            groundwater_recharge_monthly=swat_result["groundwater_recharge_monthly"],
            water_balance=swat_result["water_balance"]
        )
        
        await self.repo.save_result(result)
        
        scenario.status = SimulationStatus.COMPLETED
        scenario.completed_at = datetime.utcnow()
        await self.repo.save_scenario(scenario)
        
        return {
            "scenario_id": scenario_id,
            "result_id": result.result_id,
            "status": "completed",
            "water_balance": swat_result["water_balance"]
        }
    
    async def run_weap_allocation(
        self,
        watershed_id: str,
        scenario_name: str,
        start_year: int,
        end_year: int,
        demand_data: Dict,
        supply_data: Dict
    ) -> Dict:
        """اجرای تخصیص آب WEAP"""
        # ایجاد سناریو
        scenario_id = str(uuid.uuid4())
        scenario = HydrologicalScenario(
            scenario_id=scenario_id,
            name=scenario_name,
            description=f"WEAP allocation for {start_year}-{end_year}",
            model_type=ModelType.WEAP,
            watershed_id=watershed_id,
            start_date=datetime(start_year, 1, 1),
            end_date=datetime(end_year, 12, 31),
            parameters={"demand": demand_data, "supply": supply_data},
            status=SimulationStatus.RUNNING
        )
        
        await self.repo.save_scenario(scenario)
        
        # اجرای WEAP
        project_name = f"weap_{watershed_id}_{scenario_id[:8]}"
        weap_result = self.weap.run_allocation(
            project_name=project_name,
            start_year=start_year,
            end_year=end_year,
            demand_data=demand_data,
            supply_data=supply_data
        )
        
        if "error" in weap_result:
            scenario.status = SimulationStatus.FAILED
            await self.repo.save_scenario(scenario)
            return weap_result
        
        scenario.status = SimulationStatus.COMPLETED
        scenario.completed_at = datetime.utcnow()
        await self.repo.save_scenario(scenario)
        
        return {
            "scenario_id": scenario_id,
            "status": "completed",
            "allocations": weap_result["allocations"],
            "performance_indicators": weap_result["performance_indicators"]
        }
    
    async def analyze_climate_scenario(
        self,
        watershed_id: str,
        scenario_name: str,
        climate_change: Dict,
        demand_growth: Dict
    ) -> Dict:
        """تحلیل سناریوی تغییر اقلیم"""
        result = self.weap.analyze_scenario(
            project_name=f"weap_{watershed_id}",
            scenario_name=scenario_name,
            climate_change=climate_change,
            demand_growth=demand_growth
        )
        
        return result
    
    async def get_water_balance(
        self,
        watershed_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """دریافت بیلان آبی حوضه"""
        results = await self.repo.get_results_by_watershed(
            watershed_id,
            start_date,
            end_date
        )
        
        if not results:
            return {"error": "No simulation results found"}
        
        # محاسبه میانگین بیلان آبی
        avg_balance = {
            "precipitation_mm": 0,
            "runoff_mm": 0,
            "evapotranspiration_mm": 0,
            "recharge_mm": 0
        }
        
        for result in results:
            for key in avg_balance:
                avg_balance[key] += result.water_balance.get(key, 0)
        
        for key in avg_balance:
            avg_balance[key] /= len(results)
        
        return {
            "watershed_id": watershed_id,
            "period": f"{start_date.date()} to {end_date.date()}",
            "average_water_balance": avg_balance,
            "num_simulations": len(results)
        }
