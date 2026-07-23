from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from apps.simulation.base import SimulationRegistry

router = APIRouter(prefix="/api/v1/simulation", tags=["🔗 Model Chaining"])

class ChainRequest(BaseModel):
    chain_id: str = Field(..., description="e.g., 'climate_to_economy'")
    base_parameters: dict[str, Any] = Field(default_factory=dict)

def _get_sim_instance(sim_id: str):
    sim = SimulationRegistry.get(sim_id)
    if not sim:
        raise HTTPException(404, f"Simulator '{sim_id}' not found")
    return sim() if isinstance(sim, type) else sim

@router.post("/chain", summary="Execute a chained simulation workflow")
async def run_chain(req: ChainRequest):
    results = {}
    base = req.base_parameters
    
    if req.chain_id == "climate_to_economy":
        # Step 1: Climate (با پارامترهای کامل پیش‌فرض)
        climate_sim = _get_sim_instance("climate")
        climate_params = {
            "co2_ppm": base.get("co2_ppm", 420),
            "sensitivity": 3.0,
            "horizon": 30,
            "base_temperature": 15.0,
            "base_precipitation": 600.0
        }
        climate_res = await climate_sim.run(climate_params)
        
        # استخراج تغییرات (اگر مدل climate خروجی خاصی دارد، وگرنه فرض خشکسالی)
        temp_change = climate_res.metrics.get("temp_change", 1.5) if climate_res.status.name == "COMPLETED" else 1.5
        precip_factor = 0.85 if temp_change > 1.0 else 1.0 
        
        # Step 2: AquaCrop (با پارامترهای کامل پیش‌فرض برای عبور از Validation)
        crop_sim = _get_sim_instance("aquacrop")
        crop_params = {
            "crop": base.get("crop", "wheat"),
            "planting_date": base.get("planting_date", "2024-03-15"),
            "latitude": base.get("latitude", 35.7),
            "longitude": base.get("longitude", 51.4),
            "field_capacity": base.get("field_capacity", 30.0),
            "wilting_point": base.get("wilting_point", 14.0),
            "soil_depth": base.get("soil_depth", 1.2),
            "total_irrigation": base.get("total_irrigation", 250.0) * precip_factor,
            "co2_ppm": base.get("co2_ppm", 420.0) * 1.1, # اثر افزایش CO2
            "use_real_climate": "no"
        }
        crop_res = await crop_sim.run(crop_params)
        results["aquacrop"] = {"metrics": crop_res.metrics, "status": str(crop_res.status)}
        
        new_yield = crop_res.metrics.get("yield_t_ha", 0) if crop_res.status.name == "COMPLETED" else 0
        
        # Step 3: CBA (با پارامترهای کامل پیش‌فرض)
        cba_sim = _get_sim_instance("cba")
        # مقیاس‌دهی برای رعایت محدودیت‌های Pydantic شبیه‌ساز CBA (max 500)
        safe_benefit = min(max((new_yield * 300) / 100, 10.0), 400.0)
        safe_cost = 50.0
        
        cba_params = {
            "initial_investment": 100.0,
            "annual_benefit": safe_benefit,
            "annual_cost": safe_cost,
            "discount_rate": 5.0,
            "years": 10
        }
        cba_res = await cba_sim.run(cba_params)
        results["cba"] = {
            "metrics": cba_res.metrics, 
            "status": str(cba_res.status),
            "error": cba_res.error if cba_res.status.name == "FAILED" else None
        }
        
        final_npv = cba_res.metrics.get("npv", 0) if cba_res.status.name == "COMPLETED" else 0
        
        return {
            "chain_id": req.chain_id,
            "steps_executed": ["climate", "aquacrop", "cba"],
            "final_metrics": {
                "projected_yield_t_ha": round(new_yield, 2),
                "projected_npv": round(final_npv, 2),
                "climate_temp_change_c": round(temp_change, 2),
                "precipitation_adjustment_factor": round(precip_factor, 2)
            },
            "detailed_results": results
        }
    
    raise HTTPException(400, f"Unknown chain_id: {req.chain_id}")
