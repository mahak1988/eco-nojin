"""
ScientificModel Service Layer
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, Dict, Any
from app.models.scientific_model import ScientificModel
from app.schemas.scientific_model import ScientificModelCreate, ScientificModelUpdate
from app.services.scientific_models import MODEL_REGISTRY
from datetime import datetime


async def get_all_models(db: AsyncSession, active_only: bool = False):
    """Get all scientific models"""
    query = select(ScientificModel)
    if active_only:
        query = query.where(ScientificModel.is_active == True)
    
    result = await db.execute(query)
    models = result.scalars().all()
    
    # Get statistics
    total = len(models)
    active_count = sum(1 for m in models if m.is_active)
    featured_count = sum(1 for m in models if m.is_featured)
    
    # Count by category
    categories = {}
    for model in models:
        cat = model.category
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "models": models,
        "total": total,
        "active_count": active_count,
        "featured_count": featured_count,
        "categories": categories,
    }


async def get_model_by_id(db: AsyncSession, model_id: str):
    """Get a single scientific model by model_id"""
    result = await db.execute(
        select(ScientificModel).where(ScientificModel.model_id == model_id)
    )
    return result.scalar_one_or_none()


async def update_model(db: AsyncSession, model_id: str, update_data: ScientificModelUpdate):
    """Update a scientific model"""
    model = await get_model_by_id(db, model_id)
    if not model:
        return None
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(model, key, value)
    
    await db.commit()
    await db.refresh(model)
    return model


async def increment_usage(db: AsyncSession, model_id: str):
    """Increment usage count for a model"""
    model = await get_model_by_id(db, model_id)
    if model:
        model.usage_count += 1
        model.last_used_at = datetime.utcnow()
        await db.commit()


async def seed_scientific_models(db: AsyncSession):
    """Seed all 40 scientific models into database"""
    # Check if already seeded
    result = await db.execute(select(func.count(ScientificModel.id)))
    count = result.scalar_one()
    
    if count > 0:
        print(f"   SKIP: Already {count} models in database")
        return
    
    print("   Seeding 40 scientific models...")
    
    # Model metadata with descriptions
    model_metadata = {
        # Hydrology
        "darcy": {
            "description": "Darcy's Law describes the flow of a fluid through a porous medium. It is fundamental to hydrogeology and is used to calculate groundwater flow rates.",
            "standards": "ASTM D2434, ISO 17892-11",
            "interpretation_guide": "Higher hydraulic conductivity (K) indicates more permeable soil. Typical values: Clay (0.001-0.1 m/day), Sand (1-100 m/day), Gravel (100-1000 m/day).",
        },
        "manning": {
            "description": "Manning's Equation calculates the velocity and discharge of water in open channels. It accounts for channel roughness, hydraulic radius, and slope.",
            "standards": "USGS, FHWA HEC-22",
            "interpretation_guide": "Manning's n values: Smooth concrete (0.012), Natural streams (0.025-0.040), Heavy vegetation (0.075-0.150).",
        },
        "scs": {
            "description": "The SCS Curve Number method estimates direct runoff from rainfall events based on soil type, land use, and antecedent moisture conditions.",
            "standards": "USDA-SCS TR-55",
            "interpretation_guide": "CN values: Impervious surfaces (98), Urban areas (70-95), Forests (30-70), Pasture (40-80).",
        },
        "muskingum": {
            "description": "Muskingum routing is a hydrologic flood routing method that uses storage-discharge relationships to predict outflow hydrographs.",
            "standards": "USACE HEC-HMS",
            "interpretation_guide": "K represents travel time through reach. x ranges from 0 (reservoir) to 0.5 (pure translation).",
        },
        "rational": {
            "description": "The Rational Method is a simple approach to estimate peak discharge from small urban watersheds using rainfall intensity and runoff coefficient.",
            "standards": "ASCE, local drainage manuals",
            "interpretation_guide": "Suitable for watersheds < 200 acres. C values: Asphalt (0.95), Bare soil (0.20-0.40), Forest (0.10-0.25).",
        },
        "theis": {
            "description": "The Theis equation models transient groundwater flow to a pumping well in a confined aquifer, predicting drawdown over time.",
            "standards": "USGS Professional Paper 875",
            "interpretation_guide": "Used for aquifer test analysis. Requires long-term pumping data for accurate parameter estimation.",
        },
        "cooper_jacob": {
            "description": "Cooper-Jacob method is a simplified approximation of the Theis equation for late-time drawdown analysis in aquifer tests.",
            "standards": "USGS TWRI Book 3",
            "interpretation_guide": "Valid when u < 0.01 (late time or small r). Easier to apply than Theis for field data.",
        },
        "dupuit": {
            "description": "Dupuit-Forchheimer theory calculates seepage through earth dams assuming horizontal flow and neglecting vertical components.",
            "standards": "USACE EM 1110-2-1905",
            "interpretation_guide": "Applicable for dams with L > 2H. Assumes unconfined flow with parabolic phreatic surface.",
        },
        "kirpich": {
            "description": "Kirpich equation estimates time of concentration for small watersheds based on flow length and slope.",
            "standards": "Tennessee Highway Department",
            "interpretation_guide": "Best for agricultural watersheds with well-defined channels. Not suitable for overland flow only.",
        },
        "chow": {
            "description": "Chow's infiltration model describes the decay of infiltration rate over time using an exponential function.",
            "standards": "Ven Te Chow, Open-Channel Hydraulics",
            "interpretation_guide": "K represents steady-state infiltration rate. θ controls the rate of decay from initial to final rate.",
        },
        
        # Soil Erosion
        "rusle": {
            "description": "Revised Universal Soil Loss Equation (RUSLE) predicts average annual soil loss from sheet and rill erosion on agricultural lands.",
            "standards": "USDA-ARS Agriculture Handbook 703",
            "interpretation_guide": "Tolerable soil loss: 2-5 t/ha/yr. Values > 20 t/ha/yr indicate severe erosion requiring immediate conservation measures.",
        },
        "musle": {
            "description": "Modified Universal Soil Loss Equation (MUSLE) replaces rainfall energy with runoff parameters to estimate sediment yield for individual storm events.",
            "standards": "USDA-ARS, SWAT model",
            "interpretation_guide": "More accurate than RUSLE for single events. Used in watershed models like SWAT.",
        },
        "usle": {
            "description": "Universal Soil Loss Equation (USLE) is the original empirical model for predicting long-term average soil loss from agricultural fields.",
            "standards": "USDA-ARS Agriculture Handbook 537",
            "interpretation_guide": "Predecessor to RUSLE. Simpler but less accurate. Still used in some regions.",
        },
        "wepp": {
            "description": "Water Erosion Prediction Project (WEPP) is a process-based model that simulates interrill and rill erosion processes.",
            "standards": "USDA-ARS NSERL",
            "interpretation_guide": "More physically-based than RUSLE. Can simulate spatial and temporal variation of erosion.",
        },
        "answers": {
            "description": "Areal Nonpoint Source Watershed Environment Response Simulation (ANSWERS) models erosion and sediment transport in agricultural watersheds.",
            "standards": "Purdue University",
            "interpretation_guide": "Event-based model. Useful for evaluating BMPs and conservation practices.",
        },
        "epic": {
            "description": "Erosion-Productivity Impact Calculator (EPIC) simulates soil erosion effects on soil productivity and crop yields.",
            "standards": "USDA-ARS Temple, TX",
            "interpretation_guide": "Links erosion to crop productivity. Used for long-term sustainability assessments.",
        },
        "scsle": {
            "description": "Soil Conservation Service-Combined Soil Loss Equation (S-CSLE) extends USLE with additional conservation practice factors.",
            "standards": "Chinese Ministry of Water Resources",
            "interpretation_guide": "Widely used in China for soil conservation planning.",
        },
        "weq": {
            "description": "Wind Erosion Equation (WEQ) predicts soil loss from wind erosion based on wind speed, soil moisture, and surface conditions.",
            "standards": "USDA-SCS, NRCS",
            "interpretation_guide": "Applicable in arid and semi-arid regions. Consider roughness and vegetative cover.",
        },
        
        # Evapotranspiration
        "penman_monteith": {
            "description": "FAO-56 Penman-Monteith equation is the standard method for calculating reference evapotranspiration (ET₀) using meteorological data.",
            "standards": "FAO Irrigation and Drainage Paper 56",
            "interpretation_guide": "Gold standard for ET estimation. Requires temperature, humidity, wind speed, and solar radiation.",
        },
        "hargreaves": {
            "description": "Hargreaves equation estimates ET₀ using only temperature data and extraterrestrial radiation when other meteorological data are unavailable.",
            "standards": "FAO-56 (alternative method)",
            "interpretation_guide": "Simplified method. Accuracy ±10-15% compared to Penman-Monteith. Useful in data-scarce regions.",
        },
        "thornthwaite": {
            "description": "Thornthwaite method estimates potential evapotranspiration using only mean monthly temperature and latitude-based daylight hours.",
            "standards": "Thornthwaite (1948)",
            "interpretation_guide": "Temperature-based method. Less accurate than Penman-Monteith but requires minimal data.",
        },
        "blaney_criddle": {
            "description": "Blaney-Criddle method estimates crop water requirements using temperature, daylight hours, and crop coefficients.",
            "standards": "USDA SCS National Engineering Handbook",
            "interpretation_guide": "Simple method for irrigation scheduling. Monthly time steps recommended.",
        },
        "rice_irrigation": {
            "description": "Calculates total irrigation water requirements for rice paddies including puddling, evapotranspiration, and percolation losses.",
            "standards": "FAO-56, IRRI guidelines",
            "interpretation_guide": "Rice requires continuous flooding. Typical water requirement: 900-2500 mm per season.",
        },
        "drip": {
            "description": "Drip irrigation efficiency calculator determines gross water requirements accounting for system efficiency and distribution uniformity.",
            "standards": "ASABE, FAO-56",
            "interpretation_guide": "Drip efficiency: 85-95%. Most efficient irrigation method. Reduces water use by 30-60% compared to surface irrigation.",
        },
        "sprinkler": {
            "description": "Sprinkler irrigation efficiency calculator accounts for wind drift, evaporation losses, and system uniformity.",
            "standards": "ASABE, FAO-56",
            "interpretation_guide": "Sprinkler efficiency: 60-80%. Wind significantly affects performance. Avoid operation in high winds.",
        },
        "irrigation_req": {
            "description": "Calculates net and gross irrigation requirements based on crop evapotranspiration, effective rainfall, and system efficiency.",
            "standards": "FAO-56",
            "interpretation_guide": "Net requirement = ETc - Pe. Gross requirement accounts for losses. Essential for irrigation scheduling.",
        },
        
        # Water Quality
        "streeter_phelps": {
            "description": "Streeter-Phelps model predicts dissolved oxygen (DO) sag in streams receiving organic waste based on BOD decay and reaeration.",
            "standards": "Metcalf & Eddy, EPA",
            "interpretation_guide": "Critical DO < 4 mg/L indicates stress to aquatic life. DO < 2 mg/L is hypoxic.",
        },
        "oxygen_sag": {
            "description": "Calculates critical time and critical oxygen deficit in streams using Streeter-Phelps equations.",
            "standards": "EPA Water Quality Standards",
            "interpretation_guide": "Critical point represents worst-case DO condition. Used for permit limits and mixing zone design.",
        },
        "dilution": {
            "description": "Dilution factor calculation for effluent discharge into receiving waters using mass balance principles.",
            "standards": "EPA NPDES, local discharge permits",
            "interpretation_guide": "Higher dilution factor means better mixing. Minimum 10:1 dilution often required for thermal discharges.",
        },
        "self_purification": {
            "description": "Models the natural recovery of streams from organic pollution through biological degradation and reaeration.",
            "standards": "EPA, Metcalf & Eddy",
            "interpretation_guide": "Self-purification capacity depends on stream velocity, temperature, and turbulence.",
        },
        "eutrophication": {
            "description": "Carlson's Trophic State Index (TSI) classifies water bodies based on nutrient levels and algal biomass.",
            "standards": "Carlson (1977), EPA National Eutrophication Survey",
            "interpretation_guide": "TSI < 40: Oligotrophic (clear). 40-50: Mesotrophic. 50-70: Eutrophic (algal blooms). > 70: Hypereutrophic.",
        },
        "wqi": {
            "description": "Water Quality Index (WQI) aggregates multiple water quality parameters into a single score for easy interpretation.",
            "standards": "NSF-WQI, CCME-WQI",
            "interpretation_guide": "WQI 90-100: Excellent. 70-90: Good. 50-70: Poor. 25-50: Very Poor. < 25: Unsuitable for drinking.",
        },
        
        # Economic
        "npv": {
            "description": "Net Present Value (NPV) calculates the present value of future cash flows minus initial investment using discount rate.",
            "standards": "Corporate finance, project evaluation",
            "interpretation_guide": "NPV > 0: Accept project. NPV < 0: Reject. Higher NPV indicates more profitable investment.",
        },
        "irr": {
            "description": "Internal Rate of Return (IRR) is the discount rate that makes NPV equal to zero, representing project's expected rate of return.",
            "standards": "Corporate finance, project evaluation",
            "interpretation_guide": "IRR > cost of capital: Accept. IRR < cost of capital: Reject. Typical hurdle rates: 10-15%.",
        },
        "bc_ratio": {
            "description": "Benefit-Cost Ratio compares present value of benefits to present value of costs for project evaluation.",
            "standards": "Economic analysis, public projects",
            "interpretation_guide": "B/C > 1: Benefits exceed costs. B/C > 1.5: Highly favorable. Used for public infrastructure projects.",
        },
        "payback": {
            "description": "Payback Period calculates the time required to recover initial investment from annual cash flows.",
            "standards": "Project evaluation, investment analysis",
            "interpretation_guide": "Shorter payback preferred. Typical thresholds: 3-7 years. Does not consider time value of money.",
        },
        
        # Carbon & Ecosystem
        "carbon_seq": {
            "description": "Calculates carbon sequestration potential of reforestation and afforestation projects over time.",
            "standards": "IPCC Guidelines, Verra VCS, Gold Standard",
            "interpretation_guide": "Typical sequestration rates: Tropical forests (10-20 tCO2e/ha/yr), Temperate (3-10 tCO2e/ha/yr).",
        },
        "biodiversity": {
            "description": "Shannon Diversity Index quantifies species diversity in ecosystems using species abundance data.",
            "standards": "Ecology, conservation biology",
            "interpretation_guide": "H' < 1.5: Low diversity. 1.5-3.5: Moderate. > 3.5: High diversity. Evenness indicates distribution uniformity.",
        },
        "ecosystem_value": {
            "description": "Estimates economic value of ecosystem services including carbon sequestration, water purification, and biodiversity.",
            "standards": "TEEB, Costanza et al.",
            "interpretation_guide": "Global average: Forests ($5,000/ha/yr), Wetlands ($15,000/ha/yr), Coral reefs ($350,000/ha/yr).",
        },
        "ndvi": {
            "description": "Normalized Difference Vegetation Index (NDVI) measures vegetation health and density from satellite imagery.",
            "standards": "Remote sensing, MODIS, Landsat",
            "interpretation_guide": "NDVI < 0: Water/clouds. 0-0.2: Bare soil. 0.2-0.4: Sparse vegetation. 0.4-0.6: Moderate. > 0.6: Dense vegetation.",
        },
    }
    
    # Seed all 40 models
    for model_id, info in MODEL_REGISTRY.items():
        metadata = model_metadata.get(model_id, {})
        
        model = ScientificModel(
            model_id=model_id,
            name=info["name"],
            category=info["category"],
            description=metadata.get("description", f"{info['name']} calculation model"),
            formula=info["func"](info["input"](**_get_example_input(model_id))).formula if model_id in ["darcy", "rusle", "manning"] else None,
            interpretation_guide=metadata.get("interpretation_guide", "See model documentation for interpretation guidelines."),
            standards=metadata.get("standards", "Industry standard"),
            is_active=True,
            is_featured=(model_id in ["darcy", "rusle", "penman_monteith", "npv", "carbon_seq"]),
            default_parameters=_get_example_input(model_id),
            usage_count=0,
        )
        db.add(model)
    
    await db.commit()
    print(f"   ✅ Seeded 40 scientific models")


def _get_example_input(model_id: str) -> dict:
    """Get example input for each model"""
    examples = {
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
        "rusle": {"r_factor": 50.0, "k_factor": 0.3, "ls_factor": 1.5, "c_factor": 0.1, "p_factor": 0.5},
        "musle": {"runoff_volume": 1000.0, "peak_flow": 5.0, "k_factor": 0.3, "ls_factor": 1.5, "c_factor": 0.1, "p_factor": 0.5},
        "usle": {"r": 50.0, "k": 0.3, "ls": 1.5, "c": 0.1, "p": 0.5},
        "wepp": {"slope_steepness": 10.0, "slope_length": 100.0, "soil_erodibility": 0.3, "cover": 0.3},
        "answers": {"rainfall_energy": 100.0, "runoff_rate": 5.0, "slope": 5.0, "soil_resistance": 10.0},
        "epic": {"wind_speed": 10.0, "soil_moisture": 30.0, "surface_roughness": 2.0, "vegetative_cover": 0.4},
        "scsle": {"r_factor": 50.0, "k_factor": 0.3, "ls_factor": 1.5, "c_factor": 0.1, "p_factor": 0.5, "tech_factor": 0.8},
        "weq": {"wind_velocity": 15.0, "soil_moisture": 20.0, "surface_roughness": 1.5, "vegetative_cover": 0.3},
        "penman_monteith": {"temperature": 25.0, "wind_speed": 2.0, "solar_radiation": 20.0, "relative_humidity": 60.0},
        "hargreaves": {"temperature_mean": 25.0, "temperature_max": 32.0, "temperature_min": 18.0, "extraterrestrial_radiation": 15.0},
        "thornthwaite": {"temperature": 20.0},
        "blaney_criddle": {"temperature": 25.0, "daylight_percentage": 8.5, "crop_coefficient": 0.7},
        "rice_irrigation": {"area_hectares": 10.0, "et_rate": 5.0, "percolation": 2.0},
        "drip": {"crop_water_requirement": 500.0, "area_hectares": 10.0, "efficiency": 0.9},
        "sprinkler": {"crop_water_requirement": 500.0, "area_hectares": 10.0, "efficiency": 0.75},
        "irrigation_req": {"et0": 6.0, "kc": 0.8, "area_hectares": 10.0},
        "streeter_phelps": {"L0": 20.0, "D0": 2.0, "k1": 0.2, "k2": 0.4, "time_days": 2.0},
        "oxygen_sag": {"L0": 20.0, "D0": 2.0, "k1": 0.2, "k2": 0.4},
        "dilution": {"effluent_flow": 1.0, "stream_flow": 10.0, "effluent_concentration": 50.0, "background_concentration": 2.0},
        "self_purification": {"initial_bod": 20.0, "k1": 0.2, "time_days": 5.0, "stream_velocity": 0.5, "distance_km": 10.0},
        "eutrophication": {"tp": 50.0, "tn": 1.5, "chlorophyll_a": 20.0},
        "wqi": {"pH": 7.2, "DO": 7.0, "BOD": 3.0, "turbidity": 5.0, "total_coliforms": 100.0},
        "npv": {"initial_investment": 100000.0, "cash_flows": [25000, 30000, 35000, 40000, 45000], "discount_rate": 10.0},
        "irr": {"initial_investment": 100000.0, "cash_flows": [25000, 30000, 35000, 40000, 45000]},
        "bc_ratio": {"benefits": [30000, 35000, 40000], "costs": [20000, 22000, 24000], "discount_rate": 10.0},
        "payback": {"initial_investment": 100000.0, "annual_cash_flow": 25000.0},
        "carbon_seq": {"area_hectares": 100.0, "sequestration_rate": 5.0, "years": 20.0},
        "biodiversity": {"species_counts": [50, 30, 20, 15, 10, 5]},
        "ecosystem_value": {"area_hectares": 100.0},
        "ndvi": {"NIR": 0.5, "RED": 0.1},
    }
    return examples.get(model_id, {})
