"""CO2FIX Wrapper for Eco Nozhin - Full Implementation"""
import logging
import math
import time
from typing import Any

from apps.simulation.base import (
    BaseSimulator, SimulationParameter, SimulationResult,
    SimulationRegistry, SimulationStatus,
)

logger = logging.getLogger(__name__)

@SimulationRegistry.register
class CO2FIXSimulator(BaseSimulator):
    @property
    def id(self) -> str: return "co2fix"
    @property
    def name(self) -> str: return "CO2FIX Carbon Sequestration Model"
    @property
    def category(self) -> str: return "carbon_cycle"
    @property
    def description(self) -> str: return "CO2FIX model for carbon sequestration in forestry and agroforestry systems. Current skeleton implementation."
    @property
    def version(self) -> str: return "1.0.0-skeleton"

    def get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="land_use_type", label="Land Use Type", type="select", 
                              options=["forest", "agroforestry", "afforestation", "reforestation", "silvopasture"], 
                              default="forest", description="Type of land use system", required=True),
            SimulationParameter(name="tree_species", label="Tree Species", type="select", 
                              options=["eucalyptus", "pine", "oak", "teak", "mixed"], 
                              default="eucalyptus", description="Dominant tree species", required=True),
            SimulationParameter(name="rotation_period", label="Rotation Period", type="int", 
                              default=15, min_value=5, max_value=100, unit="years", 
                              description="Harvest rotation period", required=True),
            SimulationParameter(name="management_intensity", label="Management Intensity", type="float", 
                              default=0.7, min_value=0.0, max_value=1.0, 
                              description="Management intensity level (0-1)", required=True),
            SimulationParameter(name="site_productivity", label="Site Productivity", type="float", 
                              default=1.0, min_value=0.1, max_value=3.0, 
                              description="Site productivity index (relative)", required=True),
            SimulationParameter(name="initial_age", label="Initial Age", type="int", 
                              default=0, min_value=0, max_value=100, unit="years", 
                              description="Initial stand age", required=True),
            SimulationParameter(name="simulation_period", label="Simulation Period", type="int", 
                              default=50, min_value=1, max_value=200, unit="years", 
                              description="Length of simulation", required=True),
        ]

    async def run(self, parameters: dict[str, Any]) -> SimulationResult:
        start = time.time()
        errors = self.validate(parameters)
        if errors:
            return SimulationResult(simulator_id=self.id, simulator_name=self.name,
                status=SimulationStatus.FAILED, parameters=parameters, error="; ".join(errors))
        
        try:
            # This is a skeleton - in the real implementation, we would run the CO2FIX model
            outputs = self._run_skeleton_simulation(parameters)
            elapsed = (time.time() - start) * 1000
            return SimulationResult(simulator_id=self.id, simulator_name=self.name,
                status=SimulationStatus.COMPLETED, parameters=parameters, outputs=outputs,
                metrics=self._calculate_metrics(outputs), charts=self._generate_charts(outputs),
                execution_time_ms=elapsed)
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return SimulationResult(simulator_id=self.id, simulator_name=self.name,
                status=SimulationStatus.FAILED, parameters=parameters, error=str(e),
                execution_time_ms=elapsed)

    def _run_skeleton_simulation(self, params: dict[str, Any]) -> dict:
        """
        Skeleton implementation - this will be replaced with real CO2FIX model
        Based on CO2FIX principles: carbon sequestration in forest and agroforestry systems
        """
        land_use_type = params.get("land_use_type", "forest")
        tree_species = params.get("tree_species", "eucalyptus")
        rotation_period = params.get("rotation_period", 15)
        management_intensity = params.get("management_intensity", 0.7)
        site_productivity = params.get("site_productivity", 1.0)
        initial_age = params.get("initial_age", 0)
        sim_period = params.get("simulation_period", 50)
        
        # Species-specific parameters based on CO2FIX concepts
        species_params = {
            "eucalyptus": {"growth_rate": 1.2, "max_age": 30, "carbon_content": 0.47},
            "pine": {"growth_rate": 0.8, "max_age": 80, "carbon_content": 0.45},
            "oak": {"growth_rate": 0.6, "max_age": 150, "carbon_content": 0.48},
            "teak": {"growth_rate": 0.9, "max_age": 60, "carbon_content": 0.46},
            "mixed": {"growth_rate": 0.85, "max_age": 50, "carbon_content": 0.47}
        }
        
        species_info = species_params.get(tree_species, species_params["eucalyptus"])
        
        # Land use type multipliers
        land_use_multipliers = {
            "forest": 1.0,
            "agroforestry": 0.8,
            "afforestation": 0.9,
            "reforestation": 1.0,
            "silvopasture": 0.7
        }
        
        # Calculate carbon sequestration over time
        years = list(range(initial_age, initial_age + sim_period))
        aboveground_carbon = []
        belowground_carbon = []
        dead_organic_carbon = []
        total_carbon = []
        
        current_age = initial_age
        for year in range(sim_period):
            # Calculate biomass based on age and growth parameters
            # Logistic growth curve
            age = current_age + year
            max_biomass = species_info["growth_rate"] * site_productivity * 20  # Max theoretical biomass
            
            # Apply logistic growth function
            growth_factor = 1 / (1 + math.exp(-0.2 * (age - species_info["max_age"]/2)))
            biomass = max_biomass * growth_factor * land_use_multipliers[land_use_type] * management_intensity
            
            # Calculate carbon components
            above_carbon = biomass * species_info["carbon_content"] * 0.7  # 70% aboveground
            below_carbon = biomass * species_info["carbon_content"] * 0.3  # 30% belowground
            doc_carbon = biomass * species_info["carbon_content"] * 0.1  # 10% dead organic matter
            
            # At rotation, reset to young stand values
            if rotation_period > 0 and (age % rotation_period) == 0 and age > 0:
                above_carbon *= 0.1  # Only 10% remains after harvest
                below_carbon *= 0.5  # 50% of roots remains
                doc_carbon *= 0.8   # Some DOC remains
            
            aboveground_carbon.append(round(above_carbon, 2))
            belowground_carbon.append(round(below_carbon, 2))
            dead_organic_carbon.append(round(doc_carbon, 2))
            total_carbon.append(round(above_carbon + below_carbon + doc_carbon, 2))
        
        # Calculate cumulative sequestration
        cumulative_carbon = []
        cumsum = 0
        for i, tc in enumerate(total_carbon):
            # Add annual increment minus losses
            increment = max(0, tc - (cumulative_carbon[-1] if cumulative_carbon else 0))
            cumsum += increment
            cumulative_carbon.append(round(cumsum, 2))
        
        # Calculate average annual sequestration
        avg_annual_seq = sum([max(0, cumulative_carbon[i] - (cumulative_carbon[i-1] if i > 0 else 0)) 
                             for i in range(len(cumulative_carbon))]) / len(cumulative_carbon) if cumulative_carbon else 0
        
        # Calculate total sequestered carbon over simulation period
        total_seq_carbon = cumulative_carbon[-1] if cumulative_carbon else 0
        
        # Calculate CO2 equivalent (multiply by 44/12)
        total_co2_equivalent = total_seq_carbon * 3.67
        
        # Carbon pools breakdown at end of simulation
        final_above = aboveground_carbon[-1] if aboveground_carbon else 0
        final_below = belowground_carbon[-1] if belowground_carbon else 0
        final_doc = dead_organic_carbon[-1] if dead_organic_carbon else 0
        
        return {
            "series": [
                {"key": "total_carbon", "label": "Total Carbon Stock (tonnes C/ha)", "color": "#10b981", 
                 "values": total_carbon, "kind": "area", "fill": True},
                {"key": "cumulative_sequestration", "label": "Cumulative Sequestration (tonnes C/ha)", "color": "#3b82f6", 
                 "values": cumulative_carbon, "kind": "line", "fill": True},
                {"key": "aboveground_carbon", "label": "Aboveground Carbon (tonnes C/ha)", "color": "#8b5cf6", 
                 "values": aboveground_carbon, "kind": "area", "fill": False},
            ],
            "metrics": {
                "land_use_type": land_use_type,
                "tree_species": tree_species,
                "rotation_period_years": rotation_period,
                "management_intensity_applied": management_intensity,
                "site_productivity_index": site_productivity,
                "simulation_period_years": sim_period,
                "average_annual_sequestration_tonnes_c_ha": round(avg_annual_seq, 2),
                "total_carbon_sequestered_tonnes_c_ha": round(total_seq_carbon, 2),
                "total_co2_equivalent_tonnes_ha": round(total_co2_equivalent, 2),
                "final_aboveground_carbon_tonnes_ha": round(final_above, 2),
                "final_belowground_carbon_tonnes_ha": round(final_below, 2),
                "final_dead_organic_carbon_tonnes_ha": round(final_doc, 2),
                "species_growth_rate_factor": species_info["growth_rate"],
                "land_use_efficiency_factor": land_use_multipliers[land_use_type],
                "biomass_carbon_ratio": species_info["carbon_content"],
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}

# Try to import from the wrapper, but provide a fallback to skeleton implementation
try:
    from .wrapper import CO2FIXWrapper, CO2FIXOutput
    from .carbon_sequestration_model import CarbonSequestrationModel
except ImportError:
    logger.warning("CO2FIX wrapper not available, using skeleton implementation")
    # Provide skeleton classes to prevent import errors
    class CO2FIXWrapper:
        pass
        
    class CO2FIXOutput:
        pass
        
    class CarbonSequestrationModel:
        pass

__all__ = ["CO2FIXWrapper", "CO2FIXOutput", "CarbonSequestrationModel", "CO2FIXSimulator"]