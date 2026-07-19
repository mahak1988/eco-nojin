"""
Simulator Registry
==================
Auto-discovers and registers all simulator implementations.
"""

from apps.simulation.base import SimulationRegistry

# Import all simulators to trigger registration via @SimulationRegistry.register
from apps.simulation.agriculture.apsim import APSIMSimulator
from apps.simulation.agriculture.dssat import DSSATSimulator
from apps.simulation.agriculture.aquacrop import AquaCropSimulator
from apps.simulation.agriculture.wofost import WOFOSTSimulator
from apps.simulation.agriculture.crop_model import CropModelSimulator
from apps.simulation.hydrology.swat import SWATSimulator
from apps.simulation.hydrology.modflow import MODFLOWSimulator
from apps.simulation.hydrology.weap import WEAPSimulator
from apps.simulation.hydrology.hecras import HECRASSimulator
from apps.simulation.hydrology.bridge import BridgeSimulator
from apps.simulation.carbon_cycle.rothc import RothCSimulator
from apps.simulation.carbon_cycle.co2fix import CO2FIXSimulator
from apps.simulation.carbon_cycle.century import CenturySimulator
from apps.simulation.economics.abm import ABMSimulator
from apps.simulation.economics.teeb import TEEBSimulator
from apps.simulation.economics.cba import CBASimulator
from apps.simulation.ecosystem_services.invest import InVESTSimulator
from apps.simulation.ecosystem_services.aries import ARIESSimulator
from apps.simulation.energy.homer import HOMERSimulator
from apps.simulation.energy.leap import LEAPSimulator
from apps.simulation.soil.epic import EPICSimulator
from apps.simulation.soil.rusle2 import RUSLE2Simulator
from apps.simulation.water_quality.qual2k import QUAL2KSimulator
from apps.simulation.water_quality.wasp import WASPSimulator
from apps.simulation.biodiversity.maxent import MaxEntSimulator
from apps.simulation.biodiversity.itree import ITreeSimulator
from apps.simulation.climate import ClimateSimulator
from apps.simulation.urban import UrbanSimulator


def register_all_simulators() -> list[dict]:
    """Register all simulators and return their metadata."""
    # All simulators are auto-registered via the decorator on import
    return SimulationRegistry.list_all()