"""
Simulator Registry
==================
Auto-discovers and registers simulators at IMPORT TIME. Robust: modules that
are missing or not yet fully implemented are skipped silently (DEBUG level) and
recorded in _FAILED for reporting, so startup stays clean while the catalogue grows.
"""

import importlib
import logging

from apps.simulation.base import SimulationRegistry

logger = logging.getLogger("econojin.registry")

SIMULATOR_MODULES: list[tuple[str, str]] = [
    ("apps.simulation.climate", "ClimateSimulator"),
    ("apps.simulation.urban", "UrbanSimulator"),
    ("apps.simulation.agriculture.apsim", "APSIMSimulator"),
    ("apps.simulation.agriculture.dssat", "DSSATSimulator"),
    ("apps.simulation.agriculture.aquacrop", "AquaCropSimulator"),
    ("apps.simulation.agriculture.wofost", "WOFOSTSimulator"),
    ("apps.simulation.agriculture.crop_model", "CropModelSimulator"),
    ("apps.simulation.hydrology.swat", "SWATSimulator"),
    ("apps.simulation.hydrology.modflow", "MODFLOWSimulator"),
    ("apps.simulation.hydrology.weap", "WEAPSimulator"),
    ("apps.simulation.hydrology.hecras", "HECRASSimulator"),
    ("apps.simulation.hydrology.bridge", "BridgeSimulator"),
    ("apps.simulation.carbon_cycle.rothc", "RothCSimulator"),
    ("apps.simulation.carbon_cycle.co2fix", "CO2FIXSimulator"),
    ("apps.simulation.carbon_cycle.century", "CenturySimulator"),
    ("apps.simulation.economics.abm", "ABMSimulator"),
    ("apps.simulation.economics.teeb", "TEEBSimulator"),
    ("apps.simulation.economics.cba", "CBASimulator"),
    ("apps.simulation.ecosystem_services.invest", "InVESTSimulator"),
    ("apps.simulation.ecosystem_services.aries", "ARIESSimulator"),
    ("apps.simulation.energy.homer", "HOMERSimulator"),
    ("apps.simulation.energy.leap", "LEAPSimulator"),
    ("apps.simulation.soil.epic", "EPICSimulator"),
    ("apps.simulation.soil.rusle2", "RUSLE2Simulator"),
    ("apps.simulation.water_quality.qual2k", "QUAL2KSimulator"),
    ("apps.simulation.water_quality.wasp", "WASPSimulator"),
    ("apps.simulation.biodiversity.maxent", "MaxEntSimulator"),
    ("apps.simulation.biodiversity.itree", "ITreeSimulator"),
]

_FAILED: list[dict] = []


def _load_all() -> tuple[int, int]:
    loaded = skipped = 0
    for mod_path, cls_name in SIMULATOR_MODULES:
        try:
            mod = importlib.import_module(mod_path)
            if hasattr(mod, cls_name):
                loaded += 1
            else:
                _FAILED.append({"module": mod_path, "reason": f"class {cls_name} not found"})
                skipped += 1
        except ModuleNotFoundError:
            logger.debug(f"⏭️  {mod_path} — not implemented (skip)")
            skipped += 1
        except Exception as e:
            # e.g. "Can't instantiate abstract class ..." → record, skip silently
            logger.debug(f"⏭️  {mod_path} — {e} (skip)")
            _FAILED.append({"module": mod_path, "reason": str(e)})
            skipped += 1
    return loaded, skipped


_LOADED, _SKIPPED = _load_all()
# یک خط خلاصه (INFO) — نه اخطار
logger.info(f"🔬 شبیه‌سازها: {_LOADED} بارگذاری، {_SKIPPED} skip")


def register_all_simulators() -> list[dict]:
    return SimulationRegistry.list_all()


def get_failed_simulators() -> list[dict]:
    """Simulators that exist but could not be registered (e.g. abstract methods)."""
    return _FAILED
