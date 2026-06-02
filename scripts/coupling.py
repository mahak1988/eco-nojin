"""Model coupling utilities for Economugin"""
from .hydrology.swat_plus import SWATPlusModel
from .soil_carbon.aquacrop import AquaCropModel
from .soil_carbon.rothc import RothCModel

def create_default_chain():
    """Create the standard SWAT+ → AquaCrop → RothC chain"""
    from .coupling_engine import ModelChain
    
    chain = ModelChain()
    chain.add_model("SWAT+", SWATPlusModel())
    chain.add_model("AquaCrop", AquaCropModel())
    chain.add_model("RothC", RothCModel())
    
    # Define data flow
    chain.connect("SWAT+", "AquaCrop", {
        "available_for_crops_mm": "available_water_mm"
    })
    chain.connect("AquaCrop", "RothC", {
        "residue_for_rothc.carbon_kg_ha": "carbon_input_kg_ha"
    })
    
    return chain
