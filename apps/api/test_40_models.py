import os
"""
Test script for all 40 scientific models.
Run this after starting the backend to verify all models work.
"""

import asyncio
import httpx
import json
from typing import Dict, Any

BACKEND_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@econojin.com"
ADMIN_PASSWORD = os.environ.get("TEST_PASSWORD", "secure_default_password")

# Example inputs for each model
MODEL_EXAMPLES = {
    # Hydrology (10)
    "darcy": {"k": 1.5, "area": 100.0, "head_difference": 5.0, "length": 50.0},
    "manning": {"n": 0.035, "hydraulic_radius": 2.5, "slope": 0.001, "area": 15.0},
    "scs": {"curve_number": 75.0, "rainfall_mm": 50.0},
    "muskingum": {"inflow_1": 10.0, "inflow_2": 15.0, "outflow_1": 8.0, "K": 2.0, "x": 0.2},
    "rational": {"runoff_coefficient": 0.5, "rainfall_intensity": 50.0, "area_hectares": 10.0},
    "theis": {"pumping_rate": 100.0, "transmissivity": 50.0, "storativity": 0.001, "time_days": 1.0, "distance": 100.0},
    "cooper_jacob": {"pumping_rate": 100.0, "transmissivity": 50.0, "time_days": 1.0, "distance": 100.0, "storativity": 0.001},
    "dupuit": {"k": 1.5, "upstream_head": 10.0, "downstream_head": 5.0, "length": 100.0, "width": 50.0},
    "kirpich": {"length_m": 1000.0, "elevation_diff_m": 50.0},
    "chow": {"K": 10.0, "theta": 5.0, "time_hr": 2.0},
    
    # Soil Erosion (8)
    "rusle": {"r_factor": 50.0, "k_factor": 0.3, "ls_factor": 1.5, "c_factor": 0.1, "p_factor": 0.5},
    "musle": {"runoff_volume": 1000.0, "peak_flow": 5.0, "k_factor": 0.3, "ls_factor": 1.5, "c_factor": 0.1, "p_factor": 0.5},
    "usle": {"r": 50.0, "k": 0.3, "ls": 1.5, "c": 0.1, "p": 0.5},
    "wepp": {"slope_steepness": 10.0, "slope_length": 100.0, "soil_erodibility": 0.3, "cover": 0.3},
    "answers": {"rainfall_energy": 100.0, "runoff_rate": 5.0, "slope": 5.0, "soil_resistance": 10.0},
    "epic": {"wind_speed": 10.0, "soil_moisture": 30.0, "surface_roughness": 2.0, "vegetative_cover": 0.4},
    "scsle": {"r_factor": 50.0, "k_factor": 0.3, "ls_factor": 1.5, "c_factor": 0.1, "p_factor": 0.5, "tech_factor": 0.8},
    "weq": {"wind_velocity": 15.0, "soil_moisture": 20.0, "surface_roughness": 1.5, "vegetative_cover": 0.3},
    
    # Evapotranspiration (8)
    "penman_monteith": {"temperature": 25.0, "wind_speed": 2.0, "solar_radiation": 20.0, "relative_humidity": 60.0},
    "hargreaves": {"temperature_mean": 25.0, "temperature_max": 32.0, "temperature_min": 18.0, "extraterrestrial_radiation": 15.0},
    "thornthwaite": {"temperature": 20.0},
    "blaney_criddle": {"temperature": 25.0, "daylight_percentage": 8.5, "crop_coefficient": 0.7},
    "rice_irrigation": {"area_hectares": 10.0, "et_rate": 5.0, "percolation": 2.0},
    "drip": {"crop_water_requirement": 500.0, "area_hectares": 10.0, "efficiency": 0.9},
    "sprinkler": {"crop_water_requirement": 500.0, "area_hectares": 10.0, "efficiency": 0.75},
    "irrigation_req": {"et0": 6.0, "kc": 0.8, "area_hectares": 10.0},
    
    # Water Quality (6)
    "streeter_phelps": {"L0": 20.0, "D0": 2.0, "k1": 0.2, "k2": 0.4, "time_days": 2.0},
    "oxygen_sag": {"L0": 20.0, "D0": 2.0, "k1": 0.2, "k2": 0.4},
    "dilution": {"effluent_flow": 1.0, "stream_flow": 10.0, "effluent_concentration": 50.0, "background_concentration": 2.0},
    "self_purification": {"initial_bod": 20.0, "k1": 0.2, "time_days": 5.0, "stream_velocity": 0.5, "distance_km": 10.0},
    "eutrophication": {"tp": 50.0, "tn": 1.5, "chlorophyll_a": 20.0},
    "wqi": {"pH": 7.2, "DO": 7.0, "BOD": 3.0, "turbidity": 5.0, "total_coliforms": 100.0},
    
    # Economic (4)
    "npv": {"initial_investment": 100000.0, "cash_flows": [25000, 30000, 35000, 40000, 45000], "discount_rate": 10.0},
    "irr": {"initial_investment": 100000.0, "cash_flows": [25000, 30000, 35000, 40000, 45000]},
    "bc_ratio": {"benefits": [30000, 35000, 40000], "costs": [20000, 22000, 24000], "discount_rate": 10.0},
    "payback": {"initial_investment": 100000.0, "annual_cash_flow": 25000.0},
    
    # Carbon & Ecosystem (4)
    "carbon_seq": {"area_hectares": 100.0, "sequestration_rate": 5.0, "years": 20.0},
    "biodiversity": {"species_counts": [50, 30, 20, 15, 10, 5]},
    "ecosystem_value": {"area_hectares": 100.0},
    "ndvi": {"NIR": 0.5, "RED": 0.1},
}


async def get_token() -> str:
    """Get admin JWT token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.text}")
        return response.json()["access_token"]


async def test_model(client: httpx.AsyncClient, headers: Dict[str, str], model_id: str, example: Dict[str, Any]) -> Dict[str, Any]:
    """Test a single model"""
    try:
        response = await client.post(
            f"{BACKEND_URL}/api/v1/models/{model_id}/calculate",
            json=example,
            headers=headers,
            timeout=10.0
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "model_id": model_id,
                "status": "PASS",
                "model_name": result.get("model_name", "Unknown"),
                "category": result.get("category", "Unknown"),
                "interpretation": result.get("interpretation", ""),
            }
        else:
            return {
                "model_id": model_id,
                "status": "FAIL",
                "error": response.text,
                "status_code": response.status_code,
            }
    except Exception as e:
        return {
            "model_id": model_id,
            "status": "ERROR",
            "error": str(e),
        }


async def main():
    print("=" * 80)
    print("🧪 Testing 40 Scientific Models")
    print("=" * 80)
    
    # Get token
    print("\n🔐 Getting admin token...")
    try:
        token = await get_token()
        print(f"   ✅ Token obtained")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test list endpoint
    print("\n📋 Testing list endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/api/v1/models/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {data['total']} models in {len(data['categories'])} categories")
            for cat, count in data['category_counts'].items():
                print(f"      • {cat}: {count} models")
        else:
            print(f"   ❌ Failed: {response.text}")
            return
    
    # Test each model
    print(f"\n🧮 Testing {len(MODEL_EXAMPLES)} models...\n")
    
    results = []
    async with httpx.AsyncClient() as client:
        for model_id, example in MODEL_EXAMPLES.items():
            result = await test_model(client, headers, model_id, example)
            results.append(result)
            
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            if result["status"] == "PASS":
                print(f"{status_icon} [{result['category']}] {result['model_name']}")
                print(f"   → {result['interpretation']}")
            else:
                print(f"{status_icon} {model_id}: {result.get('error', 'Unknown error')}")
            print()
    
    # Summary
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] != "PASS")
    
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Total Models: {len(results)}")
    print(f"✅ Passed: {passed} ({passed/len(results)*100:.1f}%)")
    print(f"❌ Failed: {failed} ({failed/len(results)*100:.1f}%)")
    print("=" * 80)
    
    if failed == 0:
        print("\n🎉 ALL 40 MODELS WORKING CORRECTLY!")
    else:
        print(f"\n⚠️  {failed} model(s) failed. Check errors above.")


if __name__ == "__main__":
    asyncio.run(main())
