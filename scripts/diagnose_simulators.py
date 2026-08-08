"""
Diagnostic script to analyze the status of all simulators in the registry.
This script will determine why some simulators are being loaded and others are skipped.
"""

import os
import sys

# Add the current directory to the Python path to enable module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib
import inspect
from typing import Any

# Define the same list of simulator modules as in the registry
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


def diagnose_simulators() -> list[dict[str, Any]]:
    """
    Diagnose all simulators and return their status.
    """
    results = []

    for mod_path, cls_name in SIMULATOR_MODULES:
        result = {"module": mod_path, "class": cls_name, "status": "", "reason": ""}

        try:
            # Try to import the module
            mod = importlib.import_module(mod_path)

            # Check if the class exists
            if hasattr(mod, cls_name):
                simulator_class = getattr(mod, cls_name)

                # Check if it's actually a class
                if inspect.isclass(simulator_class):
                    # Check if the class is abstract
                    if inspect.isabstract(simulator_class):
                        result["status"] = "ABSTRACT"
                        result["reason"] = "Class is abstract and cannot be instantiated"
                    else:
                        # Try to instantiate the class
                        try:
                            instance = simulator_class()
                            result["status"] = "LOADED"
                            result["reason"] = "Successfully loaded and instantiated"
                        except Exception as e:
                            result["status"] = "INSTANTIATION_ERROR"
                            result["reason"] = f"Cannot instantiate: {e!s}"
                else:
                    result["status"] = "NOT_A_CLASS"
                    result["reason"] = f"Attribute {cls_name} exists but is not a class"
            else:
                result["status"] = "MISSING_CLASS"
                result["reason"] = f"Class {cls_name} does not exist in module"

        except ModuleNotFoundError:
            result["status"] = "IMPORT_ERROR"
            result["reason"] = "Module not found"
        except ImportError as e:
            result["status"] = "IMPORT_ERROR"
            result["reason"] = f"Import error: {e!s}"
        except Exception as e:
            result["status"] = "OTHER_ERROR"
            result["reason"] = f"Unexpected error: {e!s}"

        results.append(result)

    return results


def generate_markdown_report(results: list[dict[str, Any]]) -> str:
    """
    Generate a markdown report from the diagnosis results.
    """
    markdown = "# Simulator Diagnosis Report\n\n"
    markdown += "This report analyzes the status of all 28 simulators in the registry.\n\n"

    markdown += "| ماژول | کلاس | وضعیت | دلیل |\n"
    markdown += "|-------|------|--------|------|\n"

    for result in results:
        markdown += f"| {result['module']} | {result['class']} | {result['status']} | {result['reason']} |\n"

    # Count the statuses
    status_counts = {}
    for result in results:
        status = result["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    markdown += "\n## Summary\n\n"
    markdown += f"- Total simulators: {len(results)}\n"
    for status, count in sorted(status_counts.items()):
        markdown += f"- {status}: {count}\n"

    return markdown


if __name__ == "__main__":
    print("Diagnosing simulators...")
    results = diagnose_simulators()

    # Print results to console
    print("\nSimulator Status Table:")
    print("| ماژول | کلاس | وضعیت | دلیل |")
    print("|-------|------|--------|------|")
    for result in results:
        print(
            f"| {result['module']} | {result['class']} | {result['status']} | {result['reason']} |"
        )

    # Generate and save markdown report
    markdown_report = generate_markdown_report(results)

    # Ensure docs directory exists
    os.makedirs("docs", exist_ok=True)

    with open("docs/SIMULATOR_DIAGNOSIS.md", "w", encoding="utf-8") as f:
        f.write(markdown_report)

    print("\nDetailed report saved to docs/SIMULATOR_DIAGNOSIS.md")
    print(f"Total simulators analyzed: {len(results)}")

    # Count loaded vs skipped
    loaded_count = sum(1 for r in results if r["status"] == "LOADED")
    skipped_count = len(results) - loaded_count
    print(f"LOADED: {loaded_count}")
    print(f"SKIPPED: {skipped_count}")
