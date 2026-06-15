"""WEAP Model Wrapper - Water Evaluation And Planning

این ماژول Wrapper استاندارد برای مدل WEAP را فراهم می‌کند.
WEAP یک ابزار برنامه‌ریزی منابع آب برای تحلیل تخصیص آب و سناریوهای مدیریتی است.
"""
import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import numpy as np


class WEAPWrapper:
    """Wrapper برای اجرای مدل WEAP"""
    
    def __init__(self):
        self.project_dir = Path("weap_projects")
        self.project_dir.mkdir(exist_ok=True)
    
    def create_project(
        self,
        project_name: str,
        demand_sectors: List[str],
        water_sources: List[str]
    ) -> Dict:
        """ایجاد پروژه WEAP جدید"""
        project_path = self.project_dir / project_name
        project_path.mkdir(exist_ok=True)
        
        config = {
            "project_name": project_name,
            "demand_sectors": demand_sectors,
            "water_sources": water_sources,
            "created_at": datetime.utcnow().isoformat()
        }
        
        with open(project_path / "config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        return {
            "project_path": str(project_path),
            "status": "created",
            "config": config
        }
    
    def run_allocation(
        self,
        project_name: str,
        start_year: int,
        end_year: int,
        demand_data: Dict,
        supply_data: Dict
    ) -> Dict:
        """اجرای تخصیص آب WEAP"""
        project_path = self.project_dir / project_name
        
        if not project_path.exists():
            return {"error": "Project not found"}
        
        # شبیه‌سازی نتایج تخصیص آب
        years = end_year - start_year + 1
        
        np.random.seed(42)
        
        # تخصیص آب برای هر بخش (میلیون مترمکعب)
        allocations = {}
        unmet_demands = {}
        
        for sector in demand_data.keys():
            sector_alloc = []
            sector_unmet = []
            
            for year in range(years):
                demand = demand_data[sector][year] if year < len(demand_data[sector]) else demand_data[sector][-1]
                supply = supply_data.get("total_supply", [100] * years)[year]
                
                # تخصیص بر اساس اولویت
                allocated = min(demand, supply * 0.7)  # 70% سهم این بخش
                unmet = max(0, demand - allocated)
                
                sector_alloc.append(allocated)
                sector_unmet.append(unmet)
            
            allocations[sector] = sector_alloc
            unmet_demands[sector] = sector_unmet
        
        # محاسبه شاخص‌های عملکرد
        total_demand = sum(sum(demand_data[s]) for s in demand_data)
        total_allocated = sum(sum(allocations[s]) for s in allocations)
        total_unmet = sum(sum(unmet_demands[s]) for s in unmet_demands)
        
        reliability = total_allocated / total_demand if total_demand > 0 else 0
        vulnerability = total_unmet / total_demand if total_demand > 0 else 0
        
        result = {
            "project_name": project_name,
            "start_year": start_year,
            "end_year": end_year,
            "allocations": allocations,
            "unmet_demands": unmet_demands,
            "performance_indicators": {
                "reliability": round(reliability, 3),
                "vulnerability": round(vulnerability, 3),
                "total_demand_mcm": round(total_demand, 2),
                "total_allocated_mcm": round(total_allocated, 2),
                "total_unmet_mcm": round(total_unmet, 2)
            },
            "simulation_date": datetime.utcnow().isoformat()
        }
        
        # ذخیره نتایج
        with open(project_path / "allocation_results.json", "w") as f:
            json.dump(result, f, indent=2)
        
        return result
    
    def analyze_scenario(
        self,
        project_name: str,
        scenario_name: str,
        climate_change: Dict,
        demand_growth: Dict
    ) -> Dict:
        """تحلیل سناریوی WEAP"""
        project_path = self.project_dir / project_name
        
        if not project_path.exists():
            return {"error": "Project not found"}
        
        # شبیه‌سازی تأثیر تغییر اقلیم و رشد تقاضا
        np.random.seed(42)
        
        # کاهش عرضه آب due to climate change
        precipitation_change = climate_change.get("precipitation_change_percent", -10)
        temperature_change = climate_change.get("temperature_change_c", 2.0)
        
        # افزایش تبخیر due to temperature
        et_increase = temperature_change * 5  # 5% افزایش به ازای هر درجه
        
        # کاهش عرضه
        supply_reduction = abs(precipitation_change) + et_increase
        
        # رشد تقاضا
        demand_increase = demand_growth.get("annual_growth_percent", 2.0)
        
        # محاسبه شاخص‌های سناریو
        water_stress_index = (supply_reduction + demand_increase) / 2
        sustainability_score = max(0, 100 - water_stress_index)
        
        result = {
            "scenario_name": scenario_name,
            "climate_impact": {
                "precipitation_change_percent": precipitation_change,
                "temperature_change_c": temperature_change,
                "et_increase_percent": et_increase,
                "supply_reduction_percent": supply_reduction
            },
            "demand_impact": {
                "annual_growth_percent": demand_increase,
                "cumulative_growth_20_years": round((1 + demand_increase/100)**20 - 1, 3)
            },
            "indicators": {
                "water_stress_index": round(water_stress_index, 2),
                "sustainability_score": round(sustainability_score, 2),
                "risk_level": self._classify_risk(water_stress_index)
            },
            "recommendations": self._generate_recommendations(water_stress_index),
            "analysis_date": datetime.utcnow().isoformat()
        }
        
        return result
    
    def _classify_risk(self, stress_index: float) -> str:
        """طبقه‌بندی سطح ریسک"""
        if stress_index < 20:
            return "LOW"
        elif stress_index < 40:
            return "MODERATE"
        elif stress_index < 60:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _generate_recommendations(self, stress_index: float) -> List[str]:
        """تولید توصیه‌ها بر اساس شاخص تنش"""
        recommendations = []
        
        if stress_index > 20:
            recommendations.append("افزایش بهره‌وری آب در کشاورزی")
            recommendations.append("توسعه منابع آب غیرمتعارف")
        
        if stress_index > 40:
            recommendations.append("بازنگری در الگوی کشت")
            recommendations.append("اجرای برنامه‌های حفظ آب")
        
        if stress_index > 60:
            recommendations.append("اعلام وضعیت بحرانی آب")
            recommendations.append("محدودیت فوری مصرف")
            recommendations.append("توسعه فوری منابع آب جدید")
        
        return recommendations
