"""
Dynamic Scientific Models API Endpoints
Provides 3 endpoints to access all 40 scientific models.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.services.scientific_models import MODEL_REGISTRY, ModelOutput

router = APIRouter()


@router.get("/")
async def list_models():
    """
    List all 40 scientific models with their metadata.
    
    Returns:
        - List of all models with id, name, category, and input schema
    """
    models = []
    for model_id, info in MODEL_REGISTRY.items():
        try:
            input_schema = info["input"].model_json_schema()
        except:
            input_schema = {}
        
        models.append({
            "id": model_id,
            "name": info["name"],
            "category": info["category"],
            "input_schema": input_schema,
        })
    
    # Group by category
    categories = {}
    for model in models:
        cat = model["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(model)
    
    return {
        "models": models,
        "total": len(models),
        "categories": categories,
        "category_counts": {cat: len(models) for cat, models in categories.items()},
    }


@router.get("/{model_id}")
async def get_model_details(model_id: str):
    """
    Get detailed information about a specific model.
    
    Args:
        model_id: The unique identifier of the model (e.g., "darcy", "rusle")
    
    Returns:
        - Model metadata including input schema
    """
    if model_id not in MODEL_REGISTRY:
        available = list(MODEL_REGISTRY.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_id}' not found. Available models: {available}"
        )
    
    info = MODEL_REGISTRY[model_id]
    
    try:
        input_schema = info["input"].model_json_schema()
    except:
        input_schema = {}
    
    return {
        "id": model_id,
        "name": info["name"],
        "category": info["category"],
        "input_schema": input_schema,
        "example_input": _get_example_input(model_id),
    }


@router.post("/{model_id}/calculate")
async def calculate_model(model_id: str, data: Dict[str, Any]):
    """
    Run a scientific model calculation.
    
    Args:
        model_id: The unique identifier of the model
        data: Input parameters for the model
    
    Returns:
        - Calculation results including formula and interpretation
    """
    if model_id not in MODEL_REGISTRY:
        available = list(MODEL_REGISTRY.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_id}' not found. Available models: {available}"
        )
    
    info = MODEL_REGISTRY[model_id]
    
    try:
        # Validate and parse input
        input_data = info["input"](**data)
        
        # Run calculation
        result = info["func"](input_data)
        
        # Convert to dict
        return result.model_dump()
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Calculation error: {str(e)}"
        )


def _get_example_input(model_id: str) -> Dict[str, Any]:
    """Get example input values for each model"""
    examples = {
        # Hydrology
        "darcy": {"k": 1.5, "area": 100.0, "head_difference": 5.0, "length": 50.0},
        "manning": {"n": 0.035, "hydraulic_radius": 2.5, "slope": 0.001, "area": 15.0},
        "scs": {"curve_number": 75.0, "rainfall_mm": 50.0, "initial_abstraction_ratio": 0.2},
        "muskingum": {"inflow_1": 10.0, "inflow_2": 15.0, "outflow_1": 8.0, "K": 2.0, "x": 0.2},
        "rational": {"runoff_coefficient": 0.5, "rainfall_intensity": 50.0, "area_hectares": 10.0},
        "theis": {"pumping_rate": 100.0, "transmissivity": 50.0, "storativity": 0.001, "time_days": 1.0, "distance": 100.0},
        "cooper_jacob": {"pumping_rate": 100.0, "transmissivity": 50.0, "time_days": 1.0, "distance": 100.0, "storativity": 0.001},
        "dupuit": {"k": 1.5, "upstream_head": 10.0, "downstream_head": 5.0, "length": 100.0, "width": 50.0},
        "kirpich": {"length_m": 1000.0, "elevation_diff_m": 50.0},
        "chow": {"K": 10.0, "theta": 5.0, "time_hr": 2.0},
        
        # Soil Erosion
        "rusle": {"r_factor": 50.0, "k_factor": 0.3, "ls_factor": 1.5, "c_factor": 0.1, "p_factor": 0.5},
        "musle": {"runoff_volume": 1000.0, "peak_flow": 5.0, "k_factor": 0.3, "ls_factor": 1.5, "c_factor": 0.1, "p_factor": 0.5},
        "usle": {"r": 50.0, "k": 0.3, "ls": 1.5, "c": 0.1, "p": 0.5},
        "wepp": {"slope_steepness": 10.0, "slope_length": 100.0, "soil_erodibility": 0.3, "cover": 0.3},
        "answers": {"rainfall_energy": 100.0, "runoff_rate": 5.0, "slope": 5.0, "soil_resistance": 10.0},
        "epic": {"wind_speed": 10.0, "soil_moisture": 30.0, "surface_roughness": 2.0, "vegetative_cover": 0.4},
        "scsle": {"r_factor": 50.0, "k_factor": 0.3, "ls_factor": 1.5, "c_factor": 0.1, "p_factor": 0.5, "tech_factor": 0.8},
        "weq": {"wind_velocity": 15.0, "soil_moisture": 20.0, "surface_roughness": 1.5, "vegetative_cover": 0.3},
        
        # Evapotranspiration
        "penman_monteith": {"temperature": 25.0, "wind_speed": 2.0, "solar_radiation": 20.0, "relative_humidity": 60.0, "elevation": 100.0},
        "hargreaves": {"temperature_mean": 25.0, "temperature_max": 32.0, "temperature_min": 18.0, "extraterrestrial_radiation": 15.0},
        "thornthwaite": {"temperature": 20.0, "daylight_hours": 12.0, "days_in_month": 30.0},
        "blaney_criddle": {"temperature": 25.0, "daylight_percentage": 8.5, "crop_coefficient": 0.7},
        "rice_irrigation": {"area_hectares": 10.0, "et_rate": 5.0, "percolation": 2.0, "puddling_requirement": 200.0, "growing_days": 120.0},
        "drip": {"crop_water_requirement": 500.0, "area_hectares": 10.0, "efficiency": 0.9},
        "sprinkler": {"crop_water_requirement": 500.0, "area_hectares": 10.0, "efficiency": 0.75, "wind_factor": 1.1},
        "irrigation_req": {"et0": 6.0, "kc": 0.8, "effective_rainfall": 50.0, "efficiency": 0.7, "area_hectares": 10.0},
        
        # Water Quality
        "streeter_phelps": {"L0": 20.0, "D0": 2.0, "k1": 0.2, "k2": 0.4, "time_days": 2.0},
        "oxygen_sag": {"L0": 20.0, "D0": 2.0, "k1": 0.2, "k2": 0.4},
        "dilution": {"effluent_flow": 1.0, "stream_flow": 10.0, "effluent_concentration": 50.0, "background_concentration": 2.0},
        "self_purification": {"initial_bod": 20.0, "k1": 0.2, "time_days": 5.0, "stream_velocity": 0.5, "distance_km": 10.0},
        "eutrophication": {"tp": 50.0, "tn": 1.5, "chlorophyll_a": 20.0},
        "wqi": {"pH": 7.2, "DO": 7.0, "BOD": 3.0, "turbidity": 5.0, "total_coliforms": 100.0},
        
        # Economic
        "npv": {"initial_investment": 100000.0, "cash_flows": [25000, 30000, 35000, 40000, 45000], "discount_rate": 10.0},
        "irr": {"initial_investment": 100000.0, "cash_flows": [25000, 30000, 35000, 40000, 45000]},
        "bc_ratio": {"benefits": [30000, 35000, 40000, 45000, 50000], "costs": [20000, 22000, 24000, 26000, 28000], "discount_rate": 10.0},
        "payback": {"initial_investment": 100000.0, "annual_cash_flow": 25000.0},
        
        # Carbon & Ecosystem
        "carbon_seq": {"area_hectares": 100.0, "sequestration_rate": 5.0, "years": 20.0},
        "biodiversity": {"species_counts": [50, 30, 20, 15, 10, 5]},
        "ecosystem_value": {"area_hectares": 100.0, "forest_value": 2000.0, "water_value": 3000.0, "carbon_value": 500.0},
        "ndvi": {"NIR": 0.5, "RED": 0.1},
    }
    return examples.get(model_id, {})
